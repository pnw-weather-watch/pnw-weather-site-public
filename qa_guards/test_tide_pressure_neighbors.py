#!/usr/bin/env python3
"""Guard: P_NEIGHBORS is identical in site/tide/tide.js and tide_archive/tide_archive.py, covers every station in COORDS,
lists the 4 nearest other stations by great-circle distance (nearest first), and P_NEIGHBORS_N is 2 in both.
Optional --live: also fetches 48 h of NOAA air pressure and prints which gauges use their own vs neighbor pressure."""
import json, math, re, sys, os, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js = open(os.path.join(ROOT, "tools/fast/site/tide/tide.js")).read()
py = open(os.path.join(ROOT, "tools/fast/tide_archive/tide_archive.py")).read()
fails = []
nj = json.loads(re.search(r"const P_NEIGHBORS = (\{.*?\});", js).group(1))
npy = json.loads(re.search(r"^P_NEIGHBORS = (\{.*?\})$", py, re.M).group(1))
C = json.loads(re.search(r"const COORDS = (\{.*?\});", js).group(1))
if nj != npy: fails.append("P_NEIGHBORS differs between tide.js and tide_archive.py")
if not re.search(r"const P_NEIGHBORS_N = 2;", js) or not re.search(r"^P_NEIGHBORS_N = 2$", py, re.M): fails.append("P_NEIGHBORS_N is not 2 in both")
if set(nj) != set(C): fails.append(f"P_NEIGHBORS keys != COORDS keys: {sorted(set(nj) ^ set(C))}")
def d(a, b):
    la1, lo1 = map(math.radians, C[a]); la2, lo2 = map(math.radians, C[b])
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
for s in C:
    want = sorted([o for o in C if o != s], key=lambda o: d(s, o))[:4]
    if nj.get(s) != want: fails.append(f"{s}: neighbors {nj.get(s)} != nearest {want}")
if "P_FALLBACK" in js or "P_FALLBACK" in py: fails.append("old first-hit P_FALLBACK still present")
if "begin_date={gmt(b)}" in py: fails.append("archiver air_pressure dates are not URL-encoded")
if "--live" in sys.argv:
    has = {}
    for s in C:
        u = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=air_pressure&application=pnw_weather_tides&station={s}&range=48&time_zone=gmt&units=metric&format=json&interval=h"
        try: has[s] = len(json.load(urllib.request.urlopen(u, timeout=30)).get("data") or [])
        except Exception: has[s] = 0
        time.sleep(0.2)
    for s in C:
        if has[s]: continue
        used = [n for n in nj[s] if has[n]][:2]
        print(f"  {s}: no barometer -> average of {used} ({', '.join(f'{d(s, n):.0f} km' for n in used)})")
    print(f"  own pressure: {sum(1 for s in C if has[s])}/{len(C)}")
for f in fails: print("FAIL", f)
print("test_tide_pressure_neighbors:", "PASS" if not fails else f"FAILS {len(fails)}")
sys.exit(1 if fails else 0)
