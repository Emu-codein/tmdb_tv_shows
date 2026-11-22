"""Slide 5: Netflix goes from 3.6% of all TV to 30% among streamers.

Numbers on the deck: 30% of streamer popularity from 24% of shows, over three times the next (Shahid 9%),
46% among the 10 streamers sold in the UK, about 22% with BBC One and ITV1 added, 29% with Youku and Mango TV added.
"""
import matplotlib.ticker as mt
import numpy as np
from matplotlib.patches import Patch

from tmdb_tv_shows.deck import (LIGHT_BLUE, MUTED, NETFLIX_RED, SHOWS_COL, STREAMERS, UK_STREAMERS, load, save,
                                set_theme, streamer_table, plt)

d = load()

has_net = d[d.networks_x.map(len) > 0]
sh = has_net.explode("networks_x").groupby("networks_x").agg(n=("id", "nunique"), pop=("popularity", "sum"))
sh["sh_shows"] = sh.n / len(has_net)
sh["sh_pop"] = sh["pop"] / has_net.popularity.sum()
left = sh.sort_values("sh_pop", ascending=False).head(10)
print("all TV, top 10 by share of popularity:", {k: f"{v:.1%}" for k, v in left.sh_pop.items()})

t, _ = streamer_table(d)
right = t.head(10)
nf, nxt = t.loc["Netflix"], t.iloc[1]
print(f"\n{len(STREAMERS)} streamers: Netflix {nf.sh_pop:.1%} of popularity from {nf.sh_shows:.1%} of shows; "
      f"next {t.index[1]} {nxt.sh_pop:.1%} ({nf.sh_pop / nxt.sh_pop:.1f}x)")
print("top 10:", {k: f"{v:.1%}" for k, v in right.sh_pop.items()})

checks = {"10 streamers sold in the UK": {k: STREAMERS[k] for k in UK_STREAMERS},
          "+ BBC One and ITV1": {**STREAMERS, "BBC One": ["bbc one"], "ITV1": ["itv1"]},
          "+ Youku and Mango TV": {**STREAMERS, "Youku": ["youku"], "Mango TV": ["mango tv"]}}
for label, m in checks.items():
    tt, _ = streamer_table(d, m)
    print(f"{label:28s} Netflix {tt.loc['Netflix', 'sh_pop']:.1%}")

set_theme()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.1, 5.0))
h = 0.38
for ax, tbl, streamers, xmax, fmt in [(ax1, left, False, 0.076, "{:.1%}"), (ax2, right, True, 0.36, "{:.0%}")]:
    tbl = tbl.iloc[::-1]
    for i, (name, r) in enumerate(tbl.iterrows()):
        col = NETFLIX_RED if name == "Netflix" else (LIGHT_BLUE if streamers else MUTED)
        ax.barh(i + h / 2, r.sh_pop, height=h, color=col)
        ax.barh(i - h / 2, r.sh_shows, height=h, color=SHOWS_COL)
        ax.text(r.sh_pop + xmax * 0.012, i + h / 2, fmt.format(r.sh_pop), va="center", fontsize=10)
        ax.text(r.sh_shows + xmax * 0.012, i - h / 2, fmt.format(r.sh_shows), va="center", fontsize=8, color=MUTED)
    ax.set_yticks(range(len(tbl))); ax.set_yticklabels(tbl.index); ax.set_xlim(0, xmax)
    ax.xaxis.set_major_formatter(mt.PercentFormatter(1.0, decimals=0)); ax.grid(axis="y", visible=False)
ax1.set_xticks(np.arange(0, 0.075, 0.01)); ax2.set_xticks(np.arange(0, 0.35, 0.1))
ax1.set_title(f"Across all TV, Netflix holds {left.loc['Netflix', 'sh_pop']:.1%} of popularity")
ax1.set_xlabel("Share of all shows that have a network in TMDB")
ax2.set_title(f"Among streamers, Netflix holds {nf.sh_pop:.0%} of popularity")
ax2.set_xlabel("Share of streamer popularity or shows")
ax1.legend(handles=[Patch(color=MUTED, label="Share of popularity"), Patch(color=SHOWS_COL, label="Share of shows")],
           loc="lower right")
ax2.legend(handles=[Patch(color=NETFLIX_RED, label="Netflix, share of popularity"),
                    Patch(color=LIGHT_BLUE, label="Other streamers, share of popularity"),
                    Patch(color=SHOWS_COL, label="Share of shows")], loc="lower right", fontsize=9)
fig.tight_layout()
save(fig, "slide05_streamer_share.png")
