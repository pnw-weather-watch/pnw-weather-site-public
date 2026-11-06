"""Region layer: reads regions/regions.json and installs the views, smoothing, town tiers, H/L rules, barb density,
model view lists and CA passes into Benjamin's renderer modules. fast_encode.extra_views() calls apply() at its end.
Edit regions/regions.json, not the renderers."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
RJ = os.environ.get("WX_REGIONS", os.path.normpath(os.path.join(HERE, "..", "..", "regions", "regions.json")))
R = json.load(open(RJ))

def _proj(ccrs, p):
    if p[0] == "merc": return ccrs.Mercator(central_longitude=p[1])
    return ccrs.LambertConformal(central_longitude=p[1], central_latitude=p[2], standard_parallels=tuple(p[3]))

def apply(TM, ccrs, FE=None):
    import house_style as HS
    for k in R["removed_from_benjamin"]: TM.VIEWS.pop(k.split()[0], None)
    for vid, v in R["views"].items():
        # regions.json is the window for every view, including the ones that started in temp_maps.
        d = dict(label=v["label"], size=tuple(v["size"]), proj=_proj(ccrs, v["proj"]), box=tuple(v["box"]), fast_shift=True)
        if "ll" in v: d["ll"] = tuple(v["ll"])
        if "extent" in v: d["extent"] = tuple(v["extent"])
        TM.VIEWS[vid] = d
    TM.SMOOTH.update(R["smooth"])
    for vid, (tiers, mx) in R["region_towns"].items(): TM.REGION_TOWNS[vid] = (tuple(tiers), mx)
    # [KIT] stations (regions/stations.json) are the requested towns on every region view (placed right after tier 1)
    _st = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "regions", "stations.json")))["stations"] if t["kind"] == "town"]
    TM.REQUESTED_PTS = {t["name"]: (t["name"], t["lat"], t["lon"], "r") for t in _st}
    TM.REGION_REQUESTED = tuple(dict.fromkeys(list(TM.REGION_REQUESTED) + [t["name"] for t in _st]))
    HS.HL_RADIUS_KM.update(R["hl"]["radius_km"]); HS.HL_PROMINENCE_MB.update(R["hl"]["prominence_mb"]); HS.HL_EDGE_KM.update(R["hl"]["edge_km"])
    HS.BARBS_ACROSS.update(R["barbs_across"])
    TM.CA_PASS_TOWNS = [tuple(t) for t in R.get("CA_PASS_TOWNS", [])]
    TM.CA_PASSES = {n: (p["label"], p["lat"], p["lon"], p["elev_ft"]) for n, p in R["CA_PASSES"].items()}
    if FE is not None:
        for m, vs in R["model_views"].items():
            if m in FE.MODELS: FE.MODELS[m]["views"] = tuple(vs)
        FE.GLOBAL_VIEWS = tuple(v for v in R["views"] if "global" in R["views"][v]["models"])
    return TM
