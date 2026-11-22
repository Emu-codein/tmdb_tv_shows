"""Slide 6 (Insight 1): as episodes rise, so does popularity.

Numbers on the deck: Netflix median 4.7 at 1-6 episodes to 37.0 at 51+; Spearman with popularity: episodes 0.41,
seasons 0.38, years on air 0.32, episodes per season 0.30, episode length 0.02.
The chart compares Netflix with the other platforms in the notebook's streamer lists (CLEAR + BORDER below), launched
shows with an episode count and popularity above 0 (0 cannot be drawn on a log axis).
"""
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator

from tmdb_tv_shows.deck import BANDS, INK, MUTED, NETFLIX_RED, band, launched, load, save, set_theme, plt

OTHER_PLATFORMS = "#8CC8EC"
# The platform lists used for this chart (from notebooks/eda.ipynb, section 2), not the 31-streamer set.
CLEAR = {"Netflix": ["netflix"], "Prime Video": ["prime video"], "Disney+": ["disney+"], "HBO Max": ["hbo max", "max"],
         "Apple TV+": ["apple tv+"], "Paramount+": ["paramount+"], "discovery+": ["discovery+"],
         "Disney+ Hotstar": ["disney+ hotstar"], "Viaplay": ["viaplay"], "Crave": ["crave"], "Showmax": ["showmax"],
         "Stan": ["stan"], "Starz": ["starz"], "ZEE5": ["zee5"], "TVING": ["tving"], "wavve": ["wavve"],
         "Shudder": ["shudder"], "CuriosityStream": ["curiositystream"]}
BORDER = {"Hulu": ["hulu"], "Peacock": ["peacock"], "iQiyi": ["iqiyi"], "Tencent Video": ["tencent video"],
          "Youku": ["youku"], "WeTV": ["wetv"], "Viki": ["viki"], "Viu": ["viu"], "STAR+": ["star+"], "HBO": ["hbo"],
          "Showtime": ["showtime"], "BBC iPlayer": ["bbc iplayer"], "ITVX": ["itvx"]}

d = launched(load())

# ---- Spearman with popularity (launched Netflix shows)
nf = d[d.is_netflix].copy()
nf["eps_per_season"] = nf.number_of_episodes / nf.number_of_seasons
nf["years_on_air"] = (nf.last_air_date - nf.first_air_date).dt.days / 365.25
cols = ["number_of_episodes", "number_of_seasons", "years_on_air", "eps_per_season", "episode_run_time"]
print("Spearman with popularity (Netflix):", nf[["popularity"] + cols].corr(method="spearman").popularity[cols]
      .round(2).to_dict())

# ---- boxplot data
names = {v for vs in {**CLEAR, **BORDER}.values() for v in vs}
d = d[d.is_netflix | d.networks_x.map(lambda n: any(x.lower() in names for x in n))]
d = d.dropna(subset=["number_of_episodes"])
d = d[d.popularity > 0].copy()
d["ep_band"] = band(d.number_of_episodes)
med = d.groupby(["ep_band", d.is_netflix.map({True: "Netflix", False: "other platforms"})], observed=True)
print("\nmedian popularity by band:\n", med.popularity.agg(["size", "median"]).round(1).unstack())

set_theme()
fig, ax = plt.subplots(figsize=(9, 5.6))
pos = np.arange(len(BANDS))
for off, flag, col in [(+0.2, True, NETFLIX_RED), (-0.2, False, OTHER_PLATFORMS)]:
    data = [d.loc[(d.ep_band == b) & (d.is_netflix == flag), "popularity"] for b in BANDS]
    bp = ax.boxplot(data, positions=pos + off, orientation="horizontal", widths=0.34, patch_artist=True, whis=(5, 95),
                    showfliers=False, medianprops=dict(color=INK, linewidth=2), whiskerprops=dict(color=col),
                    capprops=dict(color=col), boxprops=dict(edgecolor=col))
    for p in bp["boxes"]:
        p.set_facecolor(col)
ax.set_xscale("log"); ax.set_xlim(0.25, 220)
ax.xaxis.set_major_locator(FixedLocator([1, 10, 100])); ax.xaxis.set_major_formatter(FixedFormatter(["1", "10", "100"]))
ax.xaxis.set_minor_locator(NullLocator())
ax.invert_yaxis(); ax.set_yticks(pos); ax.set_yticklabels(BANDS); ax.set_ylabel("Episodes"); ax.grid(axis="y", visible=False)
ax.set_xlabel("Popularity (log scale: each gridline is 10 times the last)")
ax.set_title("Trend of episodes with popularity")
ax.legend(handles=[Patch(facecolor=NETFLIX_RED, label="Netflix"), Patch(facecolor=OTHER_PLATFORMS, label="Other platforms"),
                   Line2D([0], [0], color=INK, lw=2, label="Median"),
                   Line2D([0], [0], color=MUTED, lw=1.4, label="Whiskers: 5th to 95th percentile")],
          loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4, fontsize=8.5, labelcolor=INK)
fig.tight_layout()
save(fig, "slide06_run_length.png")
