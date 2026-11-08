#!/usr/bin/env python3
"""11-08: rebuild ONLY the town-name layers + number slots for the global models' Pacific NW views with the smaller
house_style.GLOBAL_PNW_TOWN_SCALE. No model data. One image per view (static/towns_<vid>_gs.png + x2), shared by the global models;
each model keeps its own grid points (fi/fj) for each town, only the label position/size changes.
  towns_global.py --manifest M.json --fixes view_fixes.json --out DIR [--check]"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fast_encode as FE, view_fixes as VF
def slots_for(TM, vid, layer_fig, i0, i1, j0, j1, rs_):
    """Like view_fixes.town_slots, plus California Passes (fast_encode.town_call: CA towns + CA passes on the "wa" drawing path).
    Pass slots carry kind="pass" with their name; grid points come from the published slots."""
    import numpy as np, matplotlib.pyplot as plt
    if vid != "capasses": return VF.town_slots(TM, vid, layer_fig, i0, i1, j0, j1, rs_)
    keepT, keepP = TM.WA_TOWNS, TM.WA_PASSES
    n0 = len(keepT[0]) if keepT else 3
    TM.WA_TOWNS = [tuple(t) + tuple(keepT[0][3:]) if n0 > 3 else tuple(t) for t in TM.CA_PASS_TOWNS]; TM.WA_PASSES = TM.CA_PASSES
    try:
        crop_la = 90.0 - np.arange(i0, i1) * rs_; crop_lo = np.mod(np.arange(j0, j1) * rs_, 360.0)
        wcols = np.where(crop_lo >= 180)[0]; tw_lo1 = crop_lo[wcols] - 360; tw_la1 = crop_la
        tw_la, _ = np.meshgrid(tw_la1, tw_lo1, indexing="ij")
        fig, ax, ky = layer_fig(); arts = TM.towns(ax, "wa", (tw_la1, tw_lo1, tw_la), lambda v: None if not np.isfinite(v) else "88") or []
        fig.canvas.draw(); r = fig.canvas.get_renderer(); Wd, Hd = fig.get_size_inches() * fig.dpi; slots = []; last = None; lastp = False
        for t in arts:
            if t.get_text() != "88": last = t.get_text(); lastp = t.get_style() == "italic"; continue
            if not t.get_visible() or last is None: continue
            bb = t.get_window_extent(r)
            slots.append(dict(name=last, kind="pass" if lastp else "town", x=bb.x0 / Wd, y=1 - (bb.y0 + bb.y1) / 2 / Hd, fi=None, fj=None, size=t.get_fontsize(), color=t.get_color()))
            t.set_visible(False)
        return fig, slots
    finally: TM.WA_TOWNS, TM.WA_PASSES = keepT, keepP

def grid_fn(m, M, ref, new):
    import numpy as np
    i0, i1, j0, j1 = M["crop"]; MD = FE.MODELS[m]
    if MD["grid"] == "ll":
        rs_ = MD.get("res") or 0.25
        return lambda la, lo: (float((90.0 - la) / rs_ - i0), float(np.mod(lo, 360.0) / rs_ - j0))
    # Lambert (NBM): projection from FE.MODELS; grid origin fitted from this model's published slots (towns known on both grids)
    import cartopy.crs as ccrs
    rad = MD.get("radius", 6371229.0); pc = ccrs.PlateCarree()
    hp = ccrs.LambertConformal(globe=ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad), **MD.get("lcc", FE.HRRR_LCC))
    known = [(new[n]["la"], new[n]["lo"], ref[n]["fi"] + i0, ref[n]["fj"] + j0) for n in ref if n in new and new[n]["la"] is not None and ref[n].get("kind", "town") == "town"]
    if len(known) < 3: return lambda la, lo: (_ for _ in ()).throw(ValueError("no reference towns for this grid"))
    P = np.array([hp.transform_point(lo, la, pc) for la, lo, _, _ in known]); FI = np.array([k[2] for k in known]); FJ = np.array([k[3] for k in known])
    ax_, bx_ = np.polyfit(FJ, P[:, 0], 1); ay_, by_ = np.polyfit(FI, P[:, 1], 1)
    def f(la, lo):
        x, y = hp.transform_point(lo, la, pc); return float(round((y - by_) / ay_) - i0), float(round((x - bx_) / ax_) - j0)
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest"); ap.add_argument("--fixes"); ap.add_argument("--out"); ap.add_argument("--group", default="global", choices=["global", "hires"]); ap.add_argument("--views", default=""); a = ap.parse_args()
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, cartopy.crs as ccrs
    import house_style as HS, temp_maps as TM
    HS.use_for_plots(); FE.extra_views(TM, ccrs)
    rep_m = "hrrr" if a.group == "hires" else "gfs"
    if a.group == "hires" and "pnwhr" in TM.VIEWS:   # same hires camera as fast_encode.static uses for HRRR/RRFS
        import regions as _regions
        h = (_regions.R["views"].get("pnwhr") or {}).get("hires")
        if h:
            p_ = h["proj"]
            TM.VIEWS["pnwhr"] = dict(TM.VIEWS["pnwhr"], proj=ccrs.LambertConformal(central_longitude=p_[1], central_latitude=p_[2], standard_parallels=tuple(p_[3])),
                                     extent=tuple(h["extent"]), ll=tuple(h["ll"]), box=tuple(h["box"]))
    man = json.load(open(a.manifest)); fx = json.load(open(a.fixes)) if a.fixes and os.path.exists(a.fixes) else {"models": {}}
    os.makedirs(f"{a.out}/static/x2", exist_ok=True); rep = {}
    gi0, gi1, gj0, gj1 = man["models"]["gfs"]["crop"]
    for vid in sorted(set(a.views.split(",")) if a.views else HS.GLOBAL_PNW_VIEWS):
        def layer_fig():
            fig, ax, ky = TM.frame(vid); cam = fig._cam; cam.snap(); HS.frame(ax); fig.set_dpi(FE.DPI)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0); fig.patches.clear(); return fig, ax, ky
        f0, s0 = slots_for(TM, vid, layer_fig, gi0, gi1, gj0, gj1, 0.25); plt.close(f0)   # current sizes (alignment check)
        with HS.town_scale(rep_m, vid): fig, s1 = slots_for(TM, vid, layer_fig, gi0, gi1, gj0, gj1, 0.25)
        png = f"static/towns_{vid}{HS.towns_suffix(rep_m)}.png"
        fig.savefig(f"{a.out}/{png}", dpi=FE.DPI, transparent=True); fig.savefig(f"{a.out}/static/x2/towns_{vid}{HS.towns_suffix(rep_m)}.png", dpi=FE.DPI * FE.X2, transparent=True); plt.close(fig)
        new = {s_["name"]: dict(s_, la=None if s_["fi"] is None else 90.0 - (s_["fi"] + gi0) * 0.25, lo=None if s_["fj"] is None else (s_["fj"] + gj0) * 0.25 - 360.0) for s_ in s1}
        for m, M in man["models"].items():
            if a.views and vid not in a.views.split(","): continue
            if not HS.small_towns(m, vid) or vid not in M.get("views", {}) or HS.towns_suffix(m) != HS.towns_suffix(rep_m): continue
            src = (fx.get("models", {}).get(m, {}).get(vid) or {}).get("towns") if vid == "pnwt" else None
            old = src or M["views"][vid].get("towns") or []
            ref = {o["name"]: o for o in old}
            # alignment: the unscaled re-render must put each number where the published slot is
            d = [max(abs(o["x"] - r["x"]), abs(o["y"] - r["y"])) for r in s0 for o in [ref.get(r["name"])] if o]
            slots = []; miss = []
            to_ij = grid_fn(m, M, ref, new)
            for nm, s_ in new.items():
                o = ref.get(nm)
                if o: slots.append(dict(o, x=s_["x"], y=s_["y"], size=s_["size"])); continue
                if s_["la"] is None: miss.append(nm); continue   # a pass with no published grid point: no number
                try: fi, fj = to_ij(s_["la"], s_["lo"])
                except ValueError: miss.append(nm); continue   # a town that now fits: its own grid point on this model
                slots.append(dict(name=nm, kind="town", x=s_["x"], y=s_["y"], fi=fi, fj=fj, size=s_["size"], color=s_["color"]))
            M["views"][vid]["towns"] = slots; M["views"][vid]["towns_png"] = png
            if vid == "pnwt" and m in fx.get("models", {}) and "pnwt" in fx["models"][m]: fx["models"][m]["pnwt"] = dict(towns=slots, towns_png=png)
            rep[f"{m}/{vid}"] = dict(old=len(old), new=len(slots), dropped=sorted(set(ref) - set(new)), max_unscaled_offset=round(max(d), 4) if d else None, matched=len(d), no_number=miss)
    json.dump(man, open(f"{a.out}/manifest.json", "w")); json.dump(fx, open(f"{a.out}/view_fixes.json", "w"), indent=1)
    json.dump(rep, open(f"{a.out}/towns_report.json", "w"), indent=1); print(json.dumps(rep))
if __name__ == "__main__": main()
