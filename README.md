# TV series popularity: TMDB data exploration

What makes a TV series popular, and how could popularity be predicted before a show launches? This repo holds the data cleaning and exploration for that question, using the open TMDB TV shows dataset, focused on Netflix titles.

## Status

Work in progress.

- **Done:** loading, cleaning and formatting the full dataset, then filtering to Netflix.
- **Next:** repeated IDs, zero placeholders and outliers, then EDA and the popularity insights.
- **Later:** an outline of the ML approach for predicting popularity before launch. No model is trained yet.

## Data

- Source: [TMDB TV shows dataset on Kaggle](https://www.kaggle.com/datasets/asaniczka/full-tmdb-tv-shows-dataset-2023-150k-shows) (`TMDB_tv_dataset_v3.csv`).
- About 168,000 rows and 29 columns, one row per show. It covers all networks, not only Netflix.
- The file is not in the repo. Download it and put it at `data/tmdb_tv_shows/TMDB_tv_dataset_v3.csv`. The `data/` folder is git-ignored.
- `popularity` is TMDB's own score. There is no views or hours-watched column.

## Setup

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Then open `notebooks/tmdb.ipynb` and select the `.venv` kernel.

## Project layout

```
notebooks/tmdb.ipynb     cleaning and exploration
src/tmdb_tv_shows/       package (cleaning code will move here)
data/                    dataset, not tracked
pyproject.toml, uv.lock  dependencies, pinned
```

## What the notebook does so far

- Loads the raw file and never changes it.
- Cleans a copy: blank text to missing, exact duplicate rows dropped, a normalised `name_clean`, list columns (genres, networks, creators and so on) split into lists, dates converted to datetime.
- Filters the cleaned data to Netflix shows (1,957 rows, 1,929 distinct shows).

## Known limits

- The dataset is a snapshot from around spring 2024 and covers all networks. Netflix shows are selected through the `networks` field, which may record the original network, not where a show can be watched.
- Some shows appear several times with different values (for example `popularity`). These repeated IDs are not resolved yet.
