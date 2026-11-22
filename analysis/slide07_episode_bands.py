"""Slide 7 (Insight 1): most streamers favour short series.

Numbers on the deck: Netflix 38% of shows at 1-6 episodes and 5% at 51+, Prime Video 3%, Disney+ 2%, Paramount+ 9%;
Tencent Video 56% and iQiyi 61% at 21-50, Shahid 36%. Top 10 of the 31 streamers by popularity, counting shows
(not episodes), shows with no episode count left out.
"""
import matplotlib.ticker as mt
import numpy as np
import pandas as pd

from tmdb_tv_shows.deck import BANDS, INK, NETFLIX_RED, SURFACE, band, load, save, set_theme, streamer_table, plt

d = load()
t, s = streamer_table(d)
e = s.explode("streamer")
e = e[e.number_of_episodes.notna() & (e.number_of_episodes > 0)]
e["band"] = band(e.number_of_episodes)
bd = pd.crosstab(e.streamer, e.band, normalize="index").loc[t.index[:10]]
print((bd * 100).round(0).to_string())

set_theme()
cols = ["#D0E3F4", "#66AADF", "#0072C9", "#0645A8", "#0C1B87"]
bd = bd.iloc[::-1]
fig, ax = plt.subplots(figsize=(8.2, 5.2))
left = np.zeros(len(bd))
for j, b in enumerate(BANDS):
    v = bd[b].to_numpy()
    ax.barh(range(len(bd)), v, left=left, color=cols[j], height=0.66, label=b, edgecolor=SURFACE, linewidth=0.6)
    for i, (l, w) in enumerate(zip(left, v)):
        if w >= 0.09:
            ax.text(l + w / 2, i, f"{w:.0%}", ha="center", va="center", fontsize=9, color=INK if j < 1 else "white")
    left += v
ax.set_yticks(range(len(bd))); ax.set_yticklabels(bd.index)
for lab in ax.get_yticklabels():
    if lab.get_text() == "Netflix":
        lab.set_color(NETFLIX_RED); lab.set_fontweight("bold")
ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(mt.PercentFormatter(1.0, decimals=0)); ax.grid(False)
ax.set_xlabel("Share of the platform's shows, by number of episodes")
ax.set_title("Shows by number of episodes, top 10 streamers")
ax.legend(title="Episodes", ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13), fontsize=9)
fig.tight_layout()
save(fig, "slide07_episode_bands.png")
