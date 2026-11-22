"""Slide 10 (Insight 2): Netflix built its non-English slate years before its rivals.

Non-English scripted shows launched per year, 2016 to 2023 (2024 is a partial year). Only shows whose one listed
network is that service, so the first air date is the launch on it. Licensed shows are not counted: the data has no
date added to a service. Deck: Netflix pulls ahead from 2018, rivals catch up in 2022 and pass Netflix in 2023.
"""
import pandas as pd

from tmdb_tv_shows.deck import BLUE, INK, MUTED, SURFACE, launched, load, save, set_theme, single_rival, plt

d = launched(load())
d = d[d.first_air_date.dt.year >= 2016].copy()
d["streamer"] = d.networks_list.apply(single_rival)
d.loc[d.is_netflix, "streamer"] = "Netflix"
sc = d[d.streamer.notna() & (d.type == "Scripted")].copy()
sc["nf"] = sc.streamer.eq("Netflix")
sc["year"] = sc.first_air_date.dt.year
one_network = sc.networks_list.apply(lambda x: isinstance(x, list) and len(x) == 1)
ne = sc[sc.original_language.ne("en") & (sc.year <= 2023) & one_network & (~sc.nf | sc.netflix_network)]
print("shows counted:", ne.nf.map({True: "Netflix", False: "rivals"}).value_counts().to_dict())
yr = pd.crosstab(ne.year, ne.nf).rename(columns={True: "Netflix", False: "Other paid streamers"})
print(yr.to_string())

set_theme()
plt.rcParams.update({"axes.grid.axis": "y"})
fig, ax = plt.subplots(figsize=(10, 5.2))
for col, c in [("Netflix", BLUE), ("Other paid streamers", MUTED)]:
    ax.plot(yr.index, yr[col], color=c, lw=2, marker="o", ms=6, markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.text(yr.index[-1] + 0.15, yr[col].iloc[-1], col, va="center", fontsize=10, color=INK)
ax.set_ylabel("Non-English scripted shows launched"); ax.set_xticks(yr.index); ax.set_ylim(0)
ax.set_xlim(yr.index[0] - 0.3, yr.index[-1] + 1.6)
ax.set_title("Netflix built its non-English slate years before its rivals")
fig.tight_layout()
save(fig, "slide10_non_english_launches.png", dpi=200)
