# Analysis behind the deck

Each script rebuilds the numbers (printed) and the chart (saved to `docs/deck/`, git-ignored) for one or more slides of
"What makes a TV series popular". Shared logic (data loading, the streamer set, the chart theme) is in
`src/tmdb_tv_shows/deck.py`. Everything starts from `clean.build()`, so the dataset must be at
`data/tmdb_tv_shows/TMDB_tv_dataset_v3.csv`.

Run one script, for example:

```
uv run python analysis/slide05_streamer_share.py
```

Or all of them:

```
for f in analysis/*.py; do uv run python "$f"; done
```

## Slide map

| Slide | Message | Script | Key numbers it prints |
|---|---|---|---|
| 3, 13 | Popularity is skewed, so log1p | `slide03_popularity_skew.py` | 1,874 launched Netflix shows, 82% below 20, median 7.3, max 1,009, skew 12.1 to 0.76; skew in training and test years |
| 4 | Across all TV, daily formats win | `slide04_all_tv.py` | 78 of the top 100 past 50 episodes, 1 Netflix show, median 290 episodes; Netflix 4th (3.6%); talk shows, news and daily soaps 4% of shows and 18% of popularity on all TV, 2% and 6% on streamers |
| 4, 5, 7 | How the 31 streamers were chosen | `streamers_match_providers.py` | 365 networks hold 90% of popularity; matches against TMDB's watch-provider list in `reference/` |
| 5 | Netflix 3.6% of all TV, 30% among streamers | `slide05_streamer_share.py` | 30% of popularity from 24% of shows, Shahid 8.6%, UK set 46%, with BBC One and ITV1 22%, with Youku and Mango TV 29% |
| 6 | As episodes rise, so does popularity | `slide06_run_length.py` | Spearman: episodes 0.41, seasons 0.38, episode length 0.02; Netflix medians 4.7 to 37.0 |
| 7 | Most streamers favour short series | `slide07_episode_bands.py` | Netflix 38% at 1-6 episodes, Tencent 56% and iQiyi 61% at 21-50 |
| 8 | Non-English shows: 39% of Netflix popularity, 21% for rivals | `slide08_non_english_share.py` | 46% vs 44% of shows; top 100: 38% vs 16% |
| 9 | Korean highest; Netflix leads on other non-English | `slide09_korean.py` | Medians 11.5/11.6, 17.3/14.4 (48 and 12 shows), 7.4/4.4, with bootstrap ranges |
| 9 (notes) | Korean lead holds after controls | `slide09_language_regression.py` | Median regression: Korean 1.35x English (1.1 to 1.6) |
| 10 | Netflix built its non-English slate first | `slide10_non_english_launches.py` | Launches per year, 374 Netflix and 293 rival shows |
| 11 | Two cases: proven stories, Korean slate | `slide11_business_cases.py` | 17 of 1,874 run 100+ episodes; long runners; adaptation and template ranks; Korean on broad streamers 3.0 (97 shows) |

In `notebooks/eda.ipynb` (not repeated here):

- **Slide 16** (synopsis sentiment and embeddings): section "Synopsis: embeddings vs sentiment". Needs
  `uv run --with sentence-transformers --with vaderSentiment`.
- **Slide 21** (data quality): section "How sparse is the data?".
- **Slides 12 to 19** (ML plan): section "From EDA to the model" holds the quick checks behind the plan. The deck
  presents the ML part as a plan, not a built model.

## Notes

- Charts are cropped of footnotes on the deck and styling may differ slightly from the deck images. The numbers match.
- `reference/tv_all.json` and `tv_gb.json` are TMDB's TV watch-provider lists (sourced from JustWatch), fetched on
  19 Nov 2026. Only a yes/no streamer label comes from them; all popularity data is the Kaggle file.
- Slide 6 compares Netflix with the platform lists used in the notebook, not the 31-streamer set.
- Slides 8 and 10 count rivals as shows on exactly one of Prime Video, Disney+, Max, Apple TV+ and Paramount+.
  Slide 9 counts any show on one of them that is not on Netflix.
