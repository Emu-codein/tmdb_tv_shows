"""Slide 9 (Insight 2): Korean shows score highest; Netflix leads on other non-English.

Numbers on the deck: median popularity of scripted shows launched 2016 on. English Netflix 11.5 vs rivals 11.6;
Korean 17.3 (48 shows) vs 14.4 (12 shows, range 10.7 to 41.4); other non-English 7.4 vs 4.4.
Rivals here: any show on Prime Video, Disney+, Max, Apple TV+ or Paramount+ that is not on Netflix.
"""
import numpy as np
from matplotlib.lines import Line2D

from tmdb_tv_shows.deck import BLUE, INK, MUTED, SURFACE, load, median_ci, save, set_theme, plt

RIVALS = {"Prime Video", "Amazon Prime Video", "Disney+", "HBO Max", "Max", "Apple TV+", "Paramount+"}
d = load()
nets = d.networks_list.apply(lambda v: v if isinstance(v, list) else [])
d["rival"] = nets.apply(lambda n: any(x in RIVALS for x in n)) & ~d.is_netflix
s = d[(d.type == "Scripted") & (d.first_air_date.dt.year >= 2016) & (d.is_netflix | d.rival)].copy()
s["grp"] = np.where(s.is_netflix, "Netflix", "Rivals")
s["lang"] = np.select([s.original_language == "en", s.original_language == "ko"], ["English", "Korean"],
                      "Other non-English")

set_theme(title_size=16)
plt.rcParams.update({"axes.grid.axis": "y"})
colour = {"Netflix": BLUE, "Rivals": MUTED}
fig, ax = plt.subplots(figsize=(13.33, 7.0))
langs = ["English", "Korean", "Other non-English"]
for i, lang in enumerate(langs):
    for g, off in [("Netflix", -0.12), ("Rivals", 0.12)]:
        x = s[(s.lang == lang) & (s.grp == g)].popularity
        med, lo, hi = median_ci(x)
        print(f"{lang:18s} {g:8s} n={len(x):4d} median {med:5.1f}  95% range {lo:5.1f} to {hi:5.1f}")
        xp = i + off
        ax.plot([xp, xp], [lo, hi], color=colour[g], lw=3, solid_capstyle="round", zorder=2)
        ax.scatter(xp, med, s=110, color=colour[g], edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.text(xp - 0.05 if g == "Netflix" else xp + 0.05, med, f"{med:.1f}", ha="right" if g == "Netflix" else "left",
                va="center", fontsize=13, color=INK, bbox=dict(fc=SURFACE, ec="none", pad=1))
ax.set_xticks(range(3)); ax.set_xticklabels(langs, fontsize=15); ax.set_xlim(-0.6, 2.6)
ax.set_ylabel("Median popularity", fontsize=14, color=MUTED); ax.tick_params(labelsize=13)
ax.set_yscale("log"); ax.set_yticks([3, 5, 10, 20, 40]); ax.set_yticklabels(["3", "5", "10", "20", "40"])
ax.minorticks_off(); ax.set_ylim(3, 70)
ax.legend([Line2D([], [], marker="o", ls="", ms=10, color=colour[g]) for g in colour],
          ["Netflix", "Other paid streamers (Prime Video, Disney+, Max, Apple TV+, Paramount+)"],
          loc="upper left", fontsize=13, labelcolor=INK)
ax.set_title("Korean shows score highest on every Western streamer; Netflix leads on other non-English")
fig.tight_layout()
save(fig, "slide09_korean.png")
