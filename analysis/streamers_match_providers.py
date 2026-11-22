"""How the 31 streamers on slides 4, 5 and 7 were chosen.

1. Take the networks holding 90% of TMDB popularity (365 networks).
2. Match their names to TMDB's TV watch-provider list (sourced from JustWatch), saved in analysis/reference/.
3. By hand, remove TV channels that appear only through their apps (Channel 4, NBC, HBO, Showtime...) and YouTube.
   The result is the STREAMERS dict in src/tmdb_tv_shows/deck.py.

The provider lists were fetched on 19 Nov 2026 from:
  GET https://api.themoviedb.org/3/watch/providers/tv?language=en-US                    -> tv_all.json
  GET https://api.themoviedb.org/3/watch/providers/tv?language=en-US&watch_region=GB    -> tv_gb.json
This script only reads the saved files, so it needs no API key.
"""
import json
import re

from tmdb_tv_shows.deck import ROOT, STREAMERS, load

REF = ROOT / "analysis" / "reference"
prov_all = [x["provider_name"] for x in json.load(open(REF / "tv_all.json"))["results"]]
prov_gb = {x["provider_name"] for x in json.load(open(REF / "tv_gb.json"))["results"]}


def norm(s):
    s = s.lower().strip()
    s = re.sub(r"\s+(amazon channel|apple tv channel|roku premium channel|standard with ads|basic with ads|"
               r"free with ads|with ads|premium|kids|vip)$", "", s)
    s = s.replace(" plus", "+").replace("plus", "+") if s.endswith("plus") else s
    return s.replace(" +", "+")


ALIAS = {"prime video": "amazon prime video", "apple tv+": "apple tv", "curiositystream": "curiosity stream",
         "hbo max": "max"}
by_norm = {}
for p in prov_all:
    by_norm.setdefault(norm(p), []).append(p)

d = load()
pop = d[["networks_x", "popularity"]].explode("networks_x").dropna().groupby("networks_x").popularity.sum()
pop = pop.sort_values(ascending=False)
k90 = int((pop.cumsum() / pop.sum() < 0.9).sum()) + 1
print(f"{len(pop):,} networks; {k90} hold 90% of popularity")

matched = []
for rank, name in enumerate(pop.index[:k90], 1):
    hits = by_norm.get(ALIAS.get(name.lower(), norm(name)), [])
    if hits:
        matched.append(name)
        uk = "  [UK]" if any(h in prov_gb for h in hits) else ""
        print(f"{rank:>3} {name:<28} -> {hits[:2]}{uk}")
print(f"\n{len(matched)} of the top {k90} networks match a provider name.")

kept = {v for vs in STREAMERS.values() for v in vs}
removed = [m for m in matched if m.lower() not in kept]
print(f"Kept as streamers: {len(STREAMERS)}. Matched but removed (TV channels' apps, YouTube): {removed}")
