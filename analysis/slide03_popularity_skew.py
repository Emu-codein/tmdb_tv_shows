"""Slide 3 (The data) and slide 13 (target): popularity is heavily skewed, the log fixes it.

Numbers on the deck: 82% of launched Netflix shows below 20, median 7.3, max 1,009, skew 12.1 raw and 0.76 after log1p.
Also checks the skew in the modelling data (2016 on) and in the training and test years.
"""
import numpy as np
from scipy.stats import skew

from tmdb_tv_shows.deck import BLUE, INK, launched, load, save, set_theme, plt

d = load()
nf = launched(d[d.is_netflix])
p = nf.popularity
lp = np.log1p(p)
print(f"launched Netflix shows {len(p):,} | median {p.median():.1f} mean {p.mean():.1f} max {p.max():,.0f}")
print(f"below 20: {(p < 20).mean():.0%} | skew raw {skew(p):.1f}, log1p {skew(lp):.2f} | shows at 0: {(p == 0).sum()}")
top = p.sort_values(ascending=False)
print(f"top 10% of shows hold {top.head(len(p) // 10).sum() / p.sum():.0%} of popularity")

print("\nSkew by slice (raw, log1p):")
yr = nf.first_air_date.dt.year
for name, s in {"2016 on": nf[yr >= 2016], "2016 to 2021": nf[yr.between(2016, 2021)],
                "2022 to 2023": nf[yr.between(2022, 2023)]}.items():
    q = s.popularity
    print(f"  {name:13s} n={len(q):5,} skew {skew(q):5.1f}  log {skew(np.log1p(q)):.2f}")

set_theme(title_size=15)
plt.rcParams.update({"axes.grid.axis": "y", "xtick.labelsize": 12, "ytick.labelsize": 12, "axes.labelsize": 13})
fig, (a, b) = plt.subplots(1, 2, figsize=(10.6, 4.6))
a.hist(p, bins=60, color=BLUE, edgecolor="#F0EAD6", linewidth=0.4)
a.set_title("Raw popularity"); a.set_xlabel("Popularity"); a.set_ylabel("Shows")
a.annotate(f"{(p < 20).mean():.0%} of shows are below 20\n(median {p.median():.1f})",
           xy=(p.median(), a.get_ylim()[1] * 0.9), xytext=(250, a.get_ylim()[1] * 0.75), fontsize=12, color=INK,
           arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
a.annotate(f"A few hits, up to {p.max():,.0f}", xy=(p.max(), 3), xytext=(560, a.get_ylim()[1] * 0.3), fontsize=12,
           color=INK, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
b.hist(lp, bins=40, color=BLUE, edgecolor="#F0EAD6", linewidth=0.4)
b.set_title("log(1 + popularity)"); b.set_xlabel("log(1 + popularity)"); b.set_ylabel("Shows")
fig.tight_layout(w_pad=3)
save(fig, "slide03_popularity_skew.png", dpi=200)
