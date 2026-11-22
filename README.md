# TV series popularity: TMDB data exploration

What makes a TV series popular, and how could popularity be predicted before a show launches? This repo holds the data cleaning and exploration for that question, using the open TMDB TV shows dataset, focused on Netflix titles.

## Status

Work in progress.

- **Done:** cleaning of the full dataset (`src/tmdb_tv_shows/clean.py`), including repeated IDs, zero placeholders and flags, and Netflix shows marked (2,031). Data quality checks on the Netflix subset are done (see `notebooks/eda.ipynb`).
- **Next:** patterns and relationships in the EDA, then the popularity insights.
- **Later:** an outline of the ML approach for predicting popularity before launch. No model is trained yet.

## Data

- Source: [TMDB TV shows dataset on Kaggle](https://www.kaggle.com/datasets/asaniczka/full-tmdb-tv-shows-dataset-2023-150k-shows) (`TMDB_tv_dataset_v3.csv`).
- 168,639 rows and 29 columns. It covers all networks, not only Netflix.
- The file is not in the repo. Download it and put it at `data/tmdb_tv_shows/TMDB_tv_dataset_v3.csv`. The `data/` folder is git-ignored.
- There is no views or hours-watched column. `popularity` is TMDB's own score, and `vote_count` and `vote_average` come from TMDB user ratings.

## Setup

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Then open `notebooks/tmdb.ipynb` and select the `.venv` kernel.

## Use the cleaning code

```python
from tmdb_tv_shows.clean import build

raw, clean, dedup, dropped = build()
netflix = dedup[dedup.is_netflix]
```

- `raw`: the file as read, never changed.
- `clean`: all cleaning applied, repeated IDs still present (167,059 rows).
- `dedup`: one row per show (164,705 rows). Use this for analysis.
- `dropped`: the 2,354 copies not kept, so nothing is lost.

If you edit `clean.py` in a running notebook, restart the kernel or use `%autoreload 2`.

## Project layout

```
src/tmdb_tv_shows/clean.py   cleaning pipeline (load, clean, flag Netflix, one row per id)
src/tmdb_tv_shows/deck.py    shared helpers for the deck scripts (streamer set, theme)
notebooks/eda.ipynb          EDA, data quality and the bridge to the ML plan
analysis/                    one script per deck slide: numbers and charts (see analysis/README.md)
data/                        dataset, not tracked
pyproject.toml, uv.lock      dependencies, pinned
```

## What the cleaning does

- Blank text becomes missing, exact duplicate rows are dropped, names are normalised into `name_clean`, list columns (genres, networks, creators and so on) are split into `_list` columns, and dates are converted to datetime.
- **Zero placeholders:** `episode_run_time` 0 becomes missing. `number_of_seasons` and `number_of_episodes` 0 become missing unless the show is Planned or In Production. `vote_average` is missing where there are no votes. `popularity` 0 is kept, it looks like a real floor.
- **Repeated IDs:** one row per show. A copy that lists Netflix is preferred. Then the latest `last_air_date` and the most complete row, in an order that depends on whether `first_air_date` differs between copies. Where only `popularity` differs, it becomes the median of the copies, and the original stays in `popularity_raw`.
- **Netflix label:** `is_netflix` is True if "netflix" is one of the `networks` (`netflix_network`, 1,929 shows) or the `homepage` is on netflix.com (`netflix_homepage`). Together that is 2,031 shows, 102 of them by homepage only. `networks` itself is never changed.
- **Flags, not fixes:** `dates_reversed` (last air date before first air date) and `votes_inconsistent` (0 votes but an average above 0).

## Known limits

- The dataset is a snapshot from around spring 2024, inferred from the latest dates and not documented. It covers all networks.
- TMDB's guidelines say `networks` typically lists only the first network to air a show, so licensed shows (for example Friends on NBC) list their original network. The netflix.com homepage rule adds shows that are on Netflix but not listed. It shows a show is on Netflix, which may not mean Netflix aired it first.
- Some Netflix shows may still be missing, if they have neither Netflix in `networks` nor a netflix.com homepage.
- Netflix is hard-coded in the cleaning (the label and the keep-one-row rule). Next time the cleaning should treat every network the same way.
- Copies of one show differ in `popularity`, probably from snapshots taken at different times. This is assumed, there is no timestamp column. One popularity reading is noisy, and the median is only used where nothing else differs.
- Left for EDA: the `popularity` floor at 0, outliers in `episode_run_time`, noisy `vote_average` for shows with few votes, and future start dates (32 rows after June 2024).
- One known duplicate show under two IDs (The Lørenskog Disappearance) is not removed, because a fix for one ID would not scale.
