"""Shared helpers for the scripts in analysis/, which rebuild the deck's charts and numbers.

Everything starts from clean.build(). Charts are written to docs/deck/ (git-ignored).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tmdb_tv_shows.clean import build

SNAPSHOT = pd.Timestamp("2024-04-04")  # latest last_air_date in the data, assumed capture date
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "deck"

# ---- chart theme (Sky deck template; Netflix red is used only for Netflix)
SURFACE, TITLE, INK, MUTED, GRID = "#F0EAD6", "#0C1B87", "#0B1226", "#5B6B84", "#DCE3EC"
BLUE, NETFLIX_RED, LIGHT_BLUE, SHOWS_COL = "#0072C9", "#C4101C", "#8EC9EE", "#B9B49F"


def set_theme(title_size=13):
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.titlecolor": TITLE, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlesize": title_size,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "x", "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "legend.frameon": False,
    })


def save(fig, name, dpi=150):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=dpi)
    plt.close(fig)
    print("saved", OUT / name)


# ---- data
_cache = None


def load():
    """One row per show (164,705), plus `networks_x`: the networks list with "Netflix" added
    for shows marked Netflix only through a netflix.com homepage. `networks` itself is unchanged."""
    global _cache
    if _cache is None:
        _, _, d, _ = build()
        d = d.copy()
        add = d.is_netflix & ~d.netflix_network
        d["networks_x"] = [(n if isinstance(n, list) else []) + (["Netflix"] if a else [])
                           for n, a in zip(d.networks_list, add)]
        _cache = d
    return _cache.copy()


def launched(d):
    """Shows with a first air date on or before the snapshot."""
    return d[d.first_air_date.notna() & (d.first_air_date <= SNAPSHOT)]


BANDS = ["1-6", "7-10", "11-20", "21-50", "51+"]


def band(episodes):
    return pd.cut(episodes, [0, 6, 10, 20, 50, np.inf], labels=BANDS)


# ---- streamer set (slides 4, 5, 7)
# Networks holding 90% of popularity (365) were matched to TMDB's watch-provider list (JustWatch), then TV channels'
# apps and YouTube were removed. See analysis/streamers_match_providers.py. Keys: platform, values: TMDB spellings.
STREAMERS = {
    "Netflix": ["netflix"], "Shahid": ["shahid"], "Prime Video": ["prime video"], "Tencent Video": ["tencent video"],
    "Disney+": ["disney+"], "iQiyi": ["iqiyi"], "Hulu": ["hulu"], "Paramount+": ["paramount+", "cbs all access"],
    "Apple TV+": ["apple tv+"], "Peacock": ["peacock"], "ViX": ["vix"], "WWE Network": ["wwe network"], "ZEE5": ["zee5"],
    "Atresplayer Premium": ["atresplayer premium"], "Voyo": ["voyo"], "discovery+": ["discovery+"],
    "Videoland": ["videoland"], "ABEMA": ["abema"], "Viaplay": ["viaplay"], "WeTV": ["wetv"], "TVING": ["tving"],
    "LINE TV": ["line tv"], "VTM GO": ["vtm go"], "Premier": ["premier"], "TV 2 Play": ["tv 2 play"],
    "ITVX": ["itvx"], "wavve": ["wavve"], "HBO Max": ["hbo max", "max"], "OPTO": ["opto"], "iWantTFC": ["iwanttfc"],
    "RTVE Play": ["rtve play"],
}
UK_STREAMERS = ["Netflix", "Shahid", "Prime Video", "Disney+", "Paramount+", "Apple TV+", "discovery+", "Viaplay",
                "ITVX", "HBO Max"]  # the 10 on TMDB's UK provider list


def on_platforms(d, mapping=STREAMERS):
    """Shows on at least one listed platform, with a `streamer` list column."""
    lookup = {v: k for k, vs in mapping.items() for v in vs}
    s = d.assign(streamer=[sorted({lookup[x.lower()] for x in n if x.lower() in lookup}) for n in d.networks_x])
    return s[s.streamer.map(len) > 0].copy()


def streamer_table(d, mapping=STREAMERS):
    """Share of shows and of popularity per platform. A show on two platforms counts for both."""
    s = on_platforms(d, mapping)
    t = s.explode("streamer").groupby("streamer").agg(n=("id", "size"), pop=("popularity", "sum"))
    t["sh_shows"] = t.n / len(s)
    t["sh_pop"] = t["pop"] / s.popularity.sum()
    return t.sort_values("sh_pop", ascending=False), s


# ---- Netflix against five Western paid streamers (insight 2, slides 8 to 10)
RIVAL_NAMES = {"Prime Video": "Prime Video", "Amazon": "Prime Video", "Disney+": "Disney+", "HBO Max": "Max",
               "Max": "Max", "Apple TV+": "Apple TV+", "Paramount+": "Paramount+"}


def single_rival(networks):
    """The rival a show is on, if it is on exactly one of the five."""
    if not isinstance(networks, list):
        return None
    s = {RIVAL_NAMES[n] for n in networks if n in RIVAL_NAMES}
    return sorted(s)[0] if len(s) == 1 else None


def median_ci(x, n_boot=2000, seed=0):
    """Median and 95% bootstrap range of the median."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    meds = [np.median(rng.choice(x, len(x))) for _ in range(n_boot)]
    return np.median(x), *np.percentile(meds, [2.5, 97.5])
