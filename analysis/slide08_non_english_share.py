"""Slide 8 (Insight 2): non-English shows bring Netflix almost twice the share of popularity they bring rivals.

Numbers on the deck: non-English share of shows Netflix 46%, rivals 44%; share of popularity from them 39% vs 21%;
top-100 check 38% vs 16%. Shows launched 2016 on, all types. Rivals: shows on exactly one of Prime Video, Disney+,
Max, Apple TV+ and Paramount+.
"""
import numpy as np
from matplotlib.patches import Patch

from tmdb_tv_shows.deck import BLUE, INK, MUTED, NETFLIX_RED, SURFACE, launched, load, save, set_theme, single_rival, plt

d = launched(load())
d = d[d.first_air_date.dt.year >= 2016].copy()
d["streamer"] = d.networks_list.apply(single_rival)
d.loc[d.is_netflix, "streamer"] = "Netflix"
d = d[d.streamer.notna()].copy()
d["not_eng"] = d.original_language.ne("en")
d["grp"] = np.where(d.streamer == "Netflix", "Netflix", "Other paid streamers")

res = {}
for g, x in d.groupby("grp"):
    res[g] = (x.not_eng.mean(), x.loc[x.not_eng, "popularity"].sum() / x.popularity.sum(), len(x))
    top = x.nlargest(100, "popularity")
    print(f"{g:21s} {len(x):5,} shows | non-English {res[g][0]:.0%} of shows, {res[g][1]:.0%} of popularity | "
          f"top 100: {top.not_eng.mean():.0%} non-English")

set_theme()
plt.rcParams.update({"hatch.linewidth": 1.2, "axes.grid.axis": "y"})
fig, ax = plt.subplots(figsize=(10, 5.2))
w = 0.34
for i, g in enumerate(["Netflix", "Other paid streamers"]):
    c = NETFLIX_RED if g == "Netflix" else BLUE
    shows, pop, n = res[g]
    ax.bar(i - w / 2 - 0.01, shows, w, facecolor=SURFACE, edgecolor=c, linewidth=2, hatch="///")
    ax.bar(i + w / 2 + 0.01, pop, w, color=c)
    ax.text(i - w / 2 - 0.01, shows + 0.012, f"{shows:.0%}", ha="center", fontsize=12, color=INK)
    ax.text(i + w / 2 + 0.01, pop + 0.012, f"{pop:.0%}", ha="center", fontsize=12, color=INK, fontweight="bold")
ax.set_xticks([0, 1], ["Netflix", "Other paid streamers"])
ax.get_xticklabels()[0].set_color(NETFLIX_RED); ax.get_xticklabels()[0].set_fontweight("bold")
ax.set_ylim(0, 0.6); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); ax.set_xlim(-0.6, 1.6)
ax.legend(handles=[Patch(facecolor=SURFACE, edgecolor=MUTED, hatch="///", label="Share of shows that are not in English"),
                   Patch(facecolor=MUTED, label="Share of total popularity from those shows")],
          loc="upper right", fontsize=10, labelcolor=INK)
ax.set_title("Non-English shows bring Netflix almost twice the share of popularity they bring rivals")
fig.tight_layout()
save(fig, "slide08_non_english_share.png", dpi=200)
