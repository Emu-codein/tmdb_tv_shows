"""Cleaning steps for the TMDB TV shows data. Same logic as the notebook cleaning cells."""

import re
from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "tmdb_tv_shows" / "TMDB_tv_dataset_v3.csv"

SUFFIX = re.compile(
    r"(inc\.?|llc|l\.l\.c\.?|ltd\.?|limited|co\.?|corp\.?|corporation|gmbh|s\.a\.?|lp|l\.p\.|pty|plc|ag|bv|b\.v\.?)",
    re.I,
)
PLAIN_LIST_COLS = ["genres", "languages", "origin_country"]
SUFFIX_LIST_COLS = ["created_by", "networks", "production_companies"]
DATE_COLS = ["first_air_date", "last_air_date"]


def load_raw(path=DATA_PATH):
    """Read the CSV as it is. Never modified."""
    return pd.read_csv(path)


def split_list(text):
    """Split 'a, b, c' into a list, gluing legal suffixes (Inc., LLC...) back on."""
    out = []
    for part in text.split(", "):
        part = part.strip()
        if out and SUFFIX.fullmatch(part):
            out[-1] = f"{out[-1]}, {part}"
        else:
            out.append(part)
    return out


def clean_data(raw):
    """Blank text to NaN, drop exact duplicate rows, episode_run_time 0 to NaN, normalise names,
    split list columns, parse dates."""
    clean = raw.copy()

    text_cols = clean.select_dtypes(include=["object", "string"]).columns
    for c in text_cols:
        clean[c] = clean[c].where(clean[c].str.strip() != "")

    clean = clean.drop_duplicates().copy()

    # 0 means missing here (House of Cards, Black Mirror have 0 minutes), so mark it as missing
    clean["episode_run_time"] = clean["episode_run_time"].replace(0, np.nan)

    # 0 seasons or episodes is only believable for shows not yet released (Planned, In Production).
    # For any other status (Ended, Returning, Canceled, Pilot) a 0 is a missing record.
    unreleased = clean.status.isin(["Planned", "In Production"])
    for c in ["number_of_seasons", "number_of_episodes"]:
        clean[c] = clean[c].where(~((clean[c] == 0) & ~unreleased))

    # votes: an average of 0 with 0 votes is "no ratings", not a rating of 0, so mark it missing.
    # 0 votes with an average above 0 is contradictory (either column could be wrong): flag, don't fix.
    clean["votes_inconsistent"] = (clean.vote_count == 0) & (clean.vote_average > 0)
    clean["vote_average"] = clean.vote_average.where(~((clean.vote_count == 0) & (clean.vote_average == 0)))

    clean["name_clean"] = clean.name.str.strip().str.lower().str.replace(r"\s+", " ", regex=True)

    for c in PLAIN_LIST_COLS:
        clean[c + "_list"] = clean[c].apply(
            lambda t: [x.strip() for x in t.split(", ")] if isinstance(t, str) else t
        )
    for c in SUFFIX_LIST_COLS:
        clean[c + "_list"] = clean[c].apply(lambda t: split_list(t) if isinstance(t, str) else t)

    for c in DATE_COLS:
        before = clean[c].isna().sum()
        clean[c] = pd.to_datetime(clean[c], format="%Y-%m-%d", errors="coerce")
        assert clean[c].isna().sum() == before, f"{c}: some dates failed to parse"

    # flag, don't fix: last_air_date before first_air_date, we can't tell which date is wrong
    # (a missing date compares as False, so it is not flagged)
    clean["dates_reversed"] = clean.last_air_date < clean.first_air_date

    return clean


def mark_netflix(clean):
    """Add is_netflix: True if 'netflix' is one of the networks (ignoring case)."""
    out = clean.copy()
    out["is_netflix"] = out.networks_list.apply(
        lambda nets: isinstance(nets, list) and "netflix" in [n.lower() for n in nets]
    )
    return out


def dedup_ids(clean, raw_columns):
    """Keep one row per id. Returns (dedup, dropped).

    Which copy is kept:
      1. a copy that lists Netflix
      2. if first_air_date is the same across copies: latest last_air_date, then most filled columns
         if first_air_date differs across copies: most filled columns, then latest last_air_date
    If popularity is the only column that differs between copies, popularity becomes the median of
    the copies. The kept row's original value stays in popularity_raw.
    Dropped copies are returned, not thrown away.
    """
    df = clean.copy()
    raw_columns = list(raw_columns)

    df["n_filled"] = df[raw_columns].notna().sum(axis=1)
    df["n_copies"] = df.groupby("id").id.transform("size")

    rep = df[df.id.duplicated(keep=False)]
    differs = rep[raw_columns].groupby("id").nunique(dropna=False) > 1
    pop_only_ids = differs.index[(differs.sum(axis=1) == 1) & differs.popularity]
    fad_differs_ids = differs.index[differs.first_air_date]

    # last_air_date as a number of days, missing = oldest
    date_num = (df.last_air_date - pd.Timestamp("1970-01-01")).dt.days.fillna(-1)
    fad_differs = df.id.isin(fad_differs_ids)
    df["_key2"] = date_num.where(~fad_differs, df.n_filled)
    df["_key3"] = df.n_filled.where(~fad_differs, date_num)

    ranked = df.sort_values(
        ["id", "is_netflix", "_key2", "_key3"], ascending=[True, False, False, False]
    ).drop(columns=["_key2", "_key3"])
    dropped = ranked[ranked.duplicated("id")]
    dedup = ranked.drop_duplicates("id").copy()

    dedup["popularity_raw"] = dedup.popularity
    med = df[df.id.isin(pop_only_ids)].groupby("id").popularity.median()
    dedup["popularity"] = dedup.id.map(med).fillna(dedup.popularity)

    return dedup, dropped


def build(raw=None, path=DATA_PATH):
    """Full pipeline. Returns raw, clean, dedup, dropped. Pass raw to skip reading the file again."""
    if raw is None:
        raw = load_raw(path)
    clean = mark_netflix(clean_data(raw))
    dedup, dropped = dedup_ids(clean, raw.columns)
    return raw, clean, dedup, dropped
