"""Town readouts at official airports, for every model and view (encoder, runner and auto-promote).

regions/town_airports.json is the one table (NOAA/NWS or NOAA AWC station metadata). Each town slot in
a model's views (kind "town") gets fi/fj = that model's grid point at the airport:
  lcc (HRRR, RRFS 3 km, NBM) and rotll (RRFS 13 km NA): nearest native point (integers);
  lat/lon globals: fractional (bilinear at the airport, like before).
Labels (x, y) never move. Towns with no airport within AIRPORT_MAX_KM of the label keep their slot.
Pure math (no cartopy) so the viewer (selection.js townPoint) computes the same index.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "..", "..", "regions", "town_airports.json")
AIRPORT_MAX_KM = 80.0

# Same constants as selection.js LCC_GRID (GRIB first grid point = row 0, south).
LCC = {
    "hrrr": dict(lon0=-97.5, lat1=38.5, R=6371229.0, dx=3000.0, lon00=-122.719528, lat00=21.138123),
    "nbm": dict(lon0=-95.0, lat1=25.0, R=6371200.0, dx=2539.703, lon00=-126.2766, lat00=19.229),
}
LCC["rrfs"] = LCC["hrrr"]
ROTLL = {"rrfsna": dict(pole_lat=35.0, pole_lon=67.0, first_lat=-36.9303, first_lon=299.0, dlat=0.1083, dlon=0.1083)}
# Lat/lon models: grid spacing in degrees. Member viewers reuse their parent's 0.25 deg crop
# (their "0.5 deg" label is the source resolution, not the stored grid).
LL_RES = {"ifs9": 0.1}

_TABLE = None


def table():
    global _TABLE
    if _TABLE is None:
        by = {}
        with open(TABLE) as f:
            for s in json.load(f)["stations"]:
                by.setdefault(s["name"], []).append(s)
        _TABLE = by
    return _TABLE


def km(la0, lo0, la1, lo1):
    dlat = (la1 - la0) * 111.32
    dlon = (lo1 - lo0) * 111.32 * math.cos(math.radians((la0 + la1) / 2.0))
    return math.hypot(dlat, dlon)


def airport(name, la=None, lo=None, max_km=AIRPORT_MAX_KM):
    """Airport record for a town. With a hint point, the closest one within max_km; without, only an unambiguous name."""
    cands = table().get(name) or []
    if not cands:
        return None
    if la is None or lo is None:
        return cands[0] if len(cands) == 1 else None
    best = min(cands, key=lambda s: km(la, lo, s["lat"], s["lon"]))
    return best if km(la, lo, best["lat"], best["lon"]) <= max_km else None


def _lambert(lon, lat, p):
    rad = math.pi / 180.0
    n = math.sin(p["lat1"] * rad)
    F = math.cos(p["lat1"] * rad) * math.tan(math.pi / 4 + p["lat1"] * rad / 2) ** n / n
    rho = lambda la: p["R"] * F / math.tan(math.pi / 4 + la * rad / 2) ** n
    th = n * (lon - p["lon0"]) * rad
    r = rho(lat)
    return r * math.sin(th), rho(p["lat1"]) - r * math.cos(th)


def _rotll(lon, lat, s):
    phi_n, lam_n = math.radians(s["pole_lat"]), math.radians(s["pole_lon"])
    lam, phi = math.radians(lon), math.radians(lat)
    dl = lam - lam_n
    phi_r = math.degrees(math.asin(max(-1.0, min(1.0, math.sin(phi_n) * math.sin(phi) + math.cos(phi_n) * math.cos(phi) * math.cos(dl)))))
    lam_r = math.degrees(math.atan2(-math.cos(phi) * math.sin(dl), math.cos(phi_n) * math.sin(phi) - math.sin(phi_n) * math.cos(phi) * math.cos(dl)))
    diff = ((lam_r % 360.0) - s["first_lon"] + 180.0) % 360.0 - 180.0
    return (phi_r - s["first_lat"]) / s["dlat"], diff / s["dlon"]


def grid_kind(m, md):
    if m in LCC or md.get("grid") == "lcc":
        return "lcc"
    if m in ROTLL or md.get("grid") == "rotll":
        return "rotll"
    return "ll"


def ll_res(m, md):
    return LL_RES.get(m, 0.25)


def grid_ij(m, md, lat, lon):
    """(fi, fj) on this model's stored crop for a lat/lon. None if the model grid is unknown."""
    crop = md.get("crop") or [0, 0, 0, 0]
    kind = grid_kind(m, md)
    if kind == "lcc":
        p = LCC.get(m)
        if not p:
            return None
        x0, y0 = _lambert(p["lon00"], p["lat00"], p)
        x, y = _lambert(lon, lat, p)
        return float(round((y - y0) / p["dx"] - crop[0])), float(round((x - x0) / p["dx"] - crop[2]))
    if kind == "rotll":
        s = ROTLL.get(m)
        if not s:
            return None
        fi, fj = _rotll(lon, lat, s)
        return float(round(fi - crop[0])), float(round(fj - crop[2]))
    res = ll_res(m, md)
    return round((90.0 - lat) / res - crop[0], 5), round((lon % 360.0) / res - crop[2], 5)


def ll_from_slot(m, md, fi, fj):
    """Inverse for lat/lon models only (used as a hint to pick between same-name airports)."""
    if grid_kind(m, md) != "ll":
        return None
    crop = md.get("crop") or [0, 0, 0, 0]
    res = ll_res(m, md)
    lat = 90.0 - (float(fi) + crop[0]) * res
    lon = (float(fj) + crop[2]) * res
    lon = lon - 360.0 if lon > 180.0 else lon
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def hints(man):
    """(view, name) -> label-area lat/lon, from the gfs slots (they always exist and are lat/lon).
    Slots carrying "la"/"lo" (written by the static step) take precedence."""
    out, by_name = {}, {}
    order = ["gfs"] + [m for m in (man.get("models") or {}) if m != "gfs"]
    for m in order:
        md = (man.get("models") or {}).get(m) or {}
        for vid, V in (md.get("views") or {}).items():
            for t in V.get("towns") or []:
                if t.get("kind") != "town":
                    continue
                ll = (t["la"], t["lo"]) if "la" in t and "lo" in t else ll_from_slot(m, md, t.get("fi", 0), t.get("fj", 0))
                if ll is None:
                    continue
                out.setdefault((vid, t["name"]), ll)
                by_name.setdefault(t["name"], ll)
    return out, by_name


def apply(man, models=None, report=None):
    """Re-pin every town slot of `models` (default: all) to its airport. Idempotent. Returns slots changed."""
    H, by_name = hints(man)
    changed = 0
    for m, md in (man.get("models") or {}).items():
        if models is not None and m not in models:
            continue
        if not isinstance(md, dict) or not md.get("crop"):
            continue
        for vid, V in (md.get("views") or {}).items():
            for t in V.get("towns") or []:
                if t.get("kind") != "town":
                    continue
                hint = H.get((vid, t["name"])) or by_name.get(t["name"])
                a = airport(t["name"], *(hint or (None, None)))
                if a is None:
                    continue
                ij = grid_ij(m, md, a["lat"], a["lon"])
                if ij is None:
                    continue
                old = (t.get("fi"), t.get("fj"))
                same = all(isinstance(o, (int, float)) and abs(o - n) < 1e-3 for o, n in zip(old, ij))
                if not same:
                    if report is not None:
                        report.append(dict(model=m, view=vid, name=t["name"], icao=a["icao"], old=list(old), new=list(ij)))
                    t["fi"], t["fj"] = ij
                    changed += 1
                t["ap"] = a["icao"]
    return changed


def site_table():
    """Slim table for the viewer (static/town_airports.json): name -> [[icao, lat, lon], ...]."""
    return {"v": 1, "max_km": AIRPORT_MAX_KM,
            "towns": {n: [[s["icao"], s["lat"], s["lon"]] for s in v] for n, v in sorted(table().items())}}


def apply_view_fixes(fx, man, report=None):
    """Same re-pin for static/view_fixes.json town overrides (the viewer lays them over the catalog)."""
    changed = 0
    H, by_name = hints(man)
    for m, views in ((fx or {}).get("models") or {}).items():
        md = (man.get("models") or {}).get(m)
        if not md or not md.get("crop"):
            continue
        for vid, V in views.items():
            if not isinstance(V, dict) or not V.get("towns"):
                continue
            for t in V["towns"]:
                if t.get("kind") != "town":
                    continue
                hint = H.get((vid, t["name"])) or by_name.get(t["name"])
                a = airport(t["name"], *(hint or (None, None)))
                if a is None:
                    continue
                ij = grid_ij(m, md, a["lat"], a["lon"])
                if ij is None:
                    continue
                old = (t.get("fi"), t.get("fj"))
                if not all(isinstance(o, (int, float)) and abs(o - n) < 1e-3 for o, n in zip(old, ij)):
                    if report is not None:
                        report.append(dict(model=m, view=vid, name=t["name"], icao=a["icao"], old=list(old), new=list(ij), via="view_fixes"))
                    t["fi"], t["fj"] = ij
                    changed += 1
                t["ap"] = a["icao"]
    return changed
