"""Slide 9 notes: is the Korean lead just genre or recency?

A median (quantile 0.5) regression of log popularity on language, holding type, genre flags and launch year fixed.
Netflix shows launched 2016 on (1,793). Languages with fewer than 30 shows are pooled as "other".
Deck notes: Korean about 1.35 times English (95% range 1.1 to 1.6); against the pooled small languages, Korean 2.7x,
English 2.0x, Spanish 1.8x, Japanese 1.5x.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from tmdb_tv_shows.deck import launched, load

d = launched(load())
n = d[d.is_netflix & (d.first_air_date.dt.year >= 2016)].copy()
n["y"] = np.log1p(n.popularity)
n["year"] = n.first_air_date.dt.year.astype(str)
big = n.original_language.value_counts()
big = big[big >= 30].index
n["lang"] = np.where(n.original_language.isin(big), n.original_language, "other")
genres = pd.Series([g for gs in n.genres_list.dropna() for g in gs]).value_counts()
gcols = []
for g in genres[genres >= 30].index:
    col = "g_" + "".join(ch if ch.isalnum() else "_" for ch in g)
    n[col] = n.genres_list.apply(lambda x, g=g: isinstance(x, list) and g in x).astype(int)
    gcols.append(col)
print(f"{len(n):,} shows | languages with 30+ shows: {list(big)}")

for ref in ["other", "en"]:
    f = f"y ~ C(lang, Treatment('{ref}')) + C(type) + C(year) + " + " + ".join(gcols)
    m = smf.quantreg(f, n).fit(q=0.5)
    p, ci = m.params.filter(like="lang"), m.conf_int()
    print(f"\nMedian regression, against '{ref}' (times = exp(coef)):")
    for k in p.index:
        name = k.split("T.")[-1].rstrip("]")
        print(f"  {name:6s} x{np.exp(p[k]):.2f}  95% range x{np.exp(ci.loc[k, 0]):.2f} to x{np.exp(ci.loc[k, 1]):.2f}")
