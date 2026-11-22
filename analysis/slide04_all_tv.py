"""Slide 4 (All TV first): across all of TMDB, daily formats win the most attention.

Numbers on the deck: 78 of the top 100 run past 50 episodes, 1 Netflix show in the top 100, median 290 episodes,
18 talk shows and 3 news, Netflix 4th by popularity behind CBS, NBC and ABC.
Speaker notes: talk shows, news and daily soaps are 4% of all TV shows but 18% of popularity, against 2% and 6% on
the 31 streamers. A daily soap is a scripted show with 100 or more episodes per season (TMDB has no soap label).
"""
import numpy as np

from tmdb_tv_shows.deck import (BANDS, INK, MUTED, NETFLIX_RED, STREAMERS, band, launched, load, on_platforms,
                                save, set_theme, plt)

d = load()
d["nf"] = d.is_netflix

# ---- top 100 of all TV
top = d.sort_values("popularity", ascending=False).head(100).copy()
top["band"] = band(top.number_of_episodes)
print(f"top 100: {(top.number_of_episodes > 50).sum()} run past 50 episodes, {(top.number_of_episodes >= 100).sum()} "
      f"have 100 or more, median {top.number_of_episodes.median():.0f} episodes, Netflix shows {top.nf.sum()}")
print("  types:", top.type.value_counts().to_dict())
sc = top[top.type == "Scripted"]
print(f"  scripted {len(sc)}, of which past 50 episodes {(sc.number_of_episodes > 50).sum()}")

# ---- top 10 networks by share of popularity (shows with a network)
has_net = d[d.networks_x.map(len) > 0]
sh = has_net.explode("networks_x").groupby("networks_x").popularity.sum() / has_net.popularity.sum()
print("\ntop 10 networks by share of popularity:", {k: f"{v:.1%}" for k, v in sh.nlargest(10).items()})

# ---- talk shows, news and daily soaps: all TV against streamers
a = launched(d).copy()
eps_per_season = a.number_of_episodes / a.number_of_seasons
a["fmt"] = np.select([a.type.eq("Talk Show"), a.type.eq("News"), a.type.eq("Scripted") & (eps_per_season >= 100)],
                     ["talk show", "news", "daily soap"], "other")
s = on_platforms(a)
for label, df in [("all TMDB", a), ("31 streamers", s), ("Netflix", a[a.is_netflix])]:
    daily = df.fmt != "other"
    print(f"{label:13s} {len(df):7,} launched shows | daily formats {daily.mean():.1%} of shows, "
          f"{df.loc[daily, 'popularity'].sum() / df.popularity.sum():.1%} of popularity")
ts = s.sort_values("popularity", ascending=False).head(100)
print("streamers' top 100 by format:", ts.fmt.value_counts().to_dict())

# ---- chart
set_theme()
nfc = top[top.nf].band.value_counts().reindex(BANDS).fillna(0)
otc = top[~top.nf].band.value_counts().reindex(BANDS).fillna(0)
fig, ax = plt.subplots(figsize=(7.8, 4.2))
y = list(range(len(BANDS)))[::-1]
ax.barh(y, nfc, color=NETFLIX_RED, height=0.62, label="Netflix")
ax.barh(y, otc, left=nfc, color=MUTED, height=0.62, label="Every other network")
for yy, n1, n2 in zip(y, nfc, otc):
    if n2 >= 2:
        ax.text(n1 + n2 / 2, yy, f"{n2:.0f}", ha="center", va="center", color="white", fontsize=10)
    ax.text(n1 + n2 + 0.8, yy, f"{n1 + n2:.0f}", va="center", fontsize=12, fontweight="bold", color=INK)
ax.set_yticks(y); ax.set_yticklabels(BANDS); ax.set_ylabel("Episodes"); ax.set_xlabel("Shows in the top 100")
ax.set_xlim(0, 85); ax.grid(False); ax.set_title("Top 100 of all TV in TMDB"); ax.legend(loc="upper right", fontsize=9)
fig.tight_layout()
save(fig, "slide04_all_tv_top100.png")
