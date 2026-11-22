"""Slide 11: two cases NOW could test, proven stories and a small Korean drama slate.

Numbers on the deck and notes: 17 of 1,874 launched Netflix shows run 100+ episodes; popular English scripted long
runners not on Netflix (Grey's Anatomy, Family Guy, SVU...); ranks of adaptations, templates and reality formats among
the 2,031 Netflix shows; Korean shows on home-market platforms (mostly TVING) score far lower on TMDB.
The adaptation and template lists are hand-picked titles: there is no adaptation flag, so counts are a floor.
"""
import numpy as np

from tmdb_tv_shows.deck import launched, load

d = load()
nf = d[d.is_netflix].copy()
nf["rank"] = nf.popularity.rank(ascending=False, method="min").astype(int)
ln = launched(nf)
print(f"Netflix shows {len(nf):,} | launched {len(ln):,} | 100+ episodes: {(ln.number_of_episodes >= 100).sum()}")

# ---- acquire: popular English scripted long runners not on Netflix
lr = launched(d)
lr = lr[~lr.is_netflix & lr.original_language.eq("en") & lr.type.eq("Scripted") & (lr.number_of_episodes >= 100)]
cols = ["name", "first_air_date", "number_of_episodes", "popularity"]
print("\nTop English scripted long runners not on Netflix (includes soaps and YouTube shows a shortlist would drop):")
print(lr.nlargest(12, "popularity")[cols].to_string(index=False))

# ---- adapt and template: ranks among Netflix shows (hand-picked titles)
titles = ["ONE PIECE", "The Witcher", "Wednesday", "The Last Kingdom", "Lupin", "All of Us Are Dead", "Castlevania",
          "Bridgerton", "Alice in Borderland", "The Sandman", "The Umbrella Academy", "Sweet Tooth",
          "The Queen's Gambit", "Arcane", "Cyberpunk: Edgerunners", "Resident Evil", "Jupiter's Legacy",
          "Cowboy Bebop", "Money Heist: Korea - Joint Economic Area", "Love Is Blind", "Too Hot to Handle",
          "Too Hot to Handle: Germany", "Love Is Blind: Brazil", "Love Is Blind: Japan"]
print("\nRanks among Netflix shows:")
print(nf[nf.name.isin(titles)].sort_values("rank")[["name", "rank", "popularity"]].to_string(index=False))

# ---- Korean: five Western rivals against a broad set of about 30 streamers, incl. home-market ones (scripted, 2016 on)
WEST = {"Prime Video", "Amazon Prime Video", "Disney+", "HBO Max", "Max", "Apple TV+", "Paramount+"}
BROAD = WEST | {"Hulu", "Peacock", "Tencent Video", "iQiyi", "iQIYI", "Youku", "Shahid", "Viu", "Crunchyroll",
                "Mango TV", "bilibili", "Viaplay", "Disney+ Hotstar", "Hotstar", "ZEE5", "JioCinema", "Globoplay", "ViX",
                "Coupang Play", "TVING", "Wavve", "U-NEXT", "Hulu Japan", "Stan", "Crave", "SonyLIV", "MX Player",
                "ALTBalaji"}
s = d[(d.type == "Scripted") & (d.first_air_date.dt.year >= 2016)].copy()
nets = s.networks_list.apply(lambda v: v if isinstance(v, list) else [])
s["lang"] = np.select([s.original_language == "en", s.original_language == "ko"], ["English", "Korean"],
                      "Other non-English")
for label, group in [("5 Western rivals", WEST), ("broad streamers", BROAD)]:
    s["g"] = np.where(s.is_netflix, "Netflix", np.where(nets.apply(lambda n: any(x in group for x in n)), label, None))
    print(f"\nScripted shows 2016 on, Netflix vs {label} (median popularity):")
    print(s[s.g.notna()].groupby(["lang", "g"]).popularity.agg(["size", "median"]).round(1).to_string())
k = s[nets.apply(lambda n: any(x in BROAD for x in n)) & ~s.is_netflix & s.lang.eq("Korean")]
print("\nwhere the broad-streamer Korean shows are:", k.networks_list.explode().value_counts().head(5).to_dict())
