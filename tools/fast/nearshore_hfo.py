#!/usr/bin/env python3
"""Nearshore wave heights for Hawaii coast towns from NOAA NWPS (Nearshore Wave Prediction System, NWS Honolulu, public domain).
Grids (NOMADS prnwps, HTSGW): CG1 whole islands ~2.6 km; CG2 Kauai, CG3 Oahu, CG4 Maui ~0.5 km. Big Island: CG1 only.
Each town gets ONE offshore sample point: the nearest wet cell at least MIN_M (400 m) seaward of the town pin on the finest grid
that covers it (towns-offshore table written into the output). Values: significant wave height, ft, hourly to 144 h.
usage: python3 nearshore_hfo.py OUT_DIR        -> OUT_DIR/nearshore/hfo.json"""
import os, sys, json, datetime as dt, urllib.request, tempfile, math
import numpy as np, eccodes
TOWNS = {"Hanalei": (22.205, -159.5), "Haleiwa": (21.593, -158.103), "Honolulu": (21.28, -157.84), "Makapuu": (21.31, -157.65),
         "Kahului": (20.895, -156.47), "Lahaina": (20.878, -156.683), "Hilo": (19.725, -155.07), "Kailua-Kona": (19.64, -155.996)}
MIN_M = 400.0; GRIDS = ["CG2", "CG3", "CG4", "CG1"]   # finest first
U = "https://nomads.ncep.noaa.gov/cgi-bin/filter_prnwps.pl?file={f}&var_HTSGW=on&all_lev=on&dir=%2Fpr.{d}%2Fhfo%2F{c}%2F{g}"
def get(d, c, g, tmp):
    f = f"hfo_nwps_{g}_{d}_{c}00.grib2"; p = os.path.join(tmp, f)
    req = urllib.request.Request(U.format(f=f, d=d, c=c, g=g), headers={"User-Agent": "Mozilla/5.0"})
    try: b = urllib.request.urlopen(req, timeout=120).read()
    except Exception: return None
    if len(b) < 5000: return None
    open(p, "wb").write(b); return p
def read(p):
    out = {}; lat = lon = None
    with open(p, "rb") as fh:
        while True:
            g = eccodes.codes_grib_new_from_file(fh)
            if g is None: break
            ni, nj = eccodes.codes_get(g, "Ni"), eccodes.codes_get(g, "Nj")
            v = eccodes.codes_get_values(g).reshape(nj, ni); miss = eccodes.codes_get(g, "missingValue"); v = np.where(v == miss, np.nan, v)
            if lat is None:
                la = eccodes.codes_get_array(g, "latitudes").reshape(nj, ni); lo = eccodes.codes_get_array(g, "longitudes").reshape(nj, ni)
                lat, lon = la, np.where(lo > 180, lo - 360, lo)
            out[eccodes.codes_get(g, "step")] = v; eccodes.codes_release(g)
    return lat, lon, out
def main():
    O = sys.argv[1]; tmp = tempfile.mkdtemp(); now = dt.datetime.utcnow()
    for back in range(0, 48, 6):
        t = now - dt.timedelta(hours=back); d, c = t.strftime("%Y%m%d"), f"{t.hour // 6 * 6:02d}"
        files = {g: get(d, c, g, tmp) for g in GRIDS}
        if files.get("CG1"): break
    else: sys.exit("no NWPS HFO run found")
    G = {g: read(p) for g, p in files.items() if p}
    tab, vals = {}, {}
    for name, (la, lo) in TOWNS.items():
        for g in GRIDS:
            if g not in G: continue
            LA, LO, S = G[g]; v0 = S[min(S)]
            if not (LA.min() <= la <= LA.max() and LO.min() <= lo <= LO.max()): continue
            dist = 6371e3 * np.hypot(np.radians(LA - la), np.radians(LO - lo) * math.cos(math.radians(la)))
            wet = np.isfinite(v0) & (dist >= MIN_M) & (dist < 6000)
            if not wet.any(): continue
            k = np.unravel_index(np.where(wet, dist, np.inf).argmin(), dist.shape)
            tab[name] = dict(grid=g, lat=round(float(LA[k]), 4), lon=round(float(LO[k]), 4), dist_m=int(dist[k]),
                             res_m=int(round(6371e3 * math.radians(abs(LA[1, 0] - LA[0, 0])))))
            vals[name] = {int(s): (None if not np.isfinite(a[k]) else round(float(a[k]) * 3.28084, 1)) for s, a in S.items()}
            break
    init = dt.datetime.strptime(d + c, "%Y%m%d%H")
    steps = sorted({s for v in vals.values() for s in v})
    res = dict(source="NOAA NWS NWPS (Honolulu), public domain", cycle=d + c, init=init.isoformat() + "Z", units="ft", min_offshore_m=MIN_M,
               towns=tab, steps=[dict(f=s, valid=(init + dt.timedelta(hours=s)).isoformat() + "Z", v={n: vals[n].get(s) for n in vals}) for s in steps])
    os.makedirs(f"{O}/nearshore", exist_ok=True); json.dump(res, open(f"{O}/nearshore/hfo.json", "w"))
    print(d + c, json.dumps(tab, indent=0))
main()
