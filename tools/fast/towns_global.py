#!/usr/bin/env python3
"""11-08: rebuild ONLY the town-name layers + number slots for the global models' Pacific NW views with the smaller
house_style.GLOBAL_PNW_TOWN_SCALE. No model data. One image per view (static/towns_<vid>_gs.png + x2), shared by the global models;
each model keeps its own grid points (fi/fj) for each town, only the label position/size changes.
  towns_global.py --manifest M.json --fixes view_fixes.json --out DIR [--check]"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fast_encode as FE, view_fixes as VF
def grid_fn(m, M, ref, new):
    import numpy as np
    i0, i1, j0, j1 = M["crop"]; MD = FE.MODELS[m]
    if MD["grid"] == "ll":
        rs_ = MD.get("res") or 0.25
        return lambda la, lo: (float((90.0 - la) / rs_ - i0), float(np.mod(lo, 360.0) / rs_ - j0))
    # Lambert (NBM): projection from FE.MODELS; grid origin fitted from this model's published slots (towns known on both grids)
    import cartopy.crs as ccrs
    rad = MD.get("radius", 6371229.0); pc = ccrs.PlateCarree()
    hp = ccrs.LambertConformal(globe=ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad), **MD["lcc"])
    known = [(new[n]["la"], new[n]["lo"], ref[n]["fi"] + i0, ref[n]["fj"] + j0) for n in ref if n in new]
    P = np.array([hp.transform_point(lo, la, pc) for la, lo, _, _ in known]); FI = np.array([k[2] for k in known]); FJ = np.array([k[3] for k in known])
    ax_, bx_ = np.polyfit(FJ, P[:, 0], 1); ay_, by_ = np.polyfit(FI, P[:, 1], 1)
    def f(la, lo):
        x, y = hp.transform_point(lo, la, pc); return float(round((y - by_) / ay_) - i0), float(round((x - bx_) / ax_) - j0)
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest"); ap.add_argument("--fixes"); ap.add_argument("--out"); a = ap.parse_args()
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, cartopy.crs as ccrs
    import house_style as HS, temp_maps as TM
    HS.use_for_plots(); FE.extra_views(TM, ccrs)
    man = json.load(open(a.manifest)); fx = json.load(open(a.fixes)) if a.fixes and os.path.exists(a.fixes) else {"models": {}}
    os.makedirs(f"{a.out}/static/x2", exist_ok=True); rep = {}
    gi0, gi1, gj0, gj1 = man["models"]["gfs"]["crop"]
    for vid in sorted(HS.GLOBAL_PNW_VIEWS):
        def layer_fig():
            fig, ax, ky = TM.frame(vid); cam = fig._cam; cam.snap(); HS.frame(ax); fig.set_dpi(FE.DPI)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0); fig.patches.clear(); return fig, ax, ky
        f0, s0 = VF.town_slots(TM, vid, layer_fig, gi0, gi1, gj0, gj1, 0.25); plt.close(f0)   # current sizes (alignment check)
        with HS.town_scale("gfs", vid): fig, s1 = VF.town_slots(TM, vid, layer_fig, gi0, gi1, gj0, gj1, 0.25)
        png = f"static/towns_{vid}_gs.png"
        fig.savefig(f"{a.out}/{png}", dpi=FE.DPI, transparent=True); fig.savefig(f"{a.out}/static/x2/towns_{vid}_gs.png", dpi=FE.DPI * FE.X2, transparent=True); plt.close(fig)
        new = {s_["name"]: dict(s_, la=90.0 - (s_["fi"] + gi0) * 0.25, lo=(s_["fj"] + gj0) * 0.25 - 360.0) for s_ in s1}
        for m, M in man["models"].items():
            if not HS.small_towns(m, vid) or vid not in M.get("views", {}): continue
            src = (fx.get("models", {}).get(m, {}).get(vid) or {}).get("towns") if vid == "pnwt" else None
            old = src or M["views"][vid].get("towns") or []
            ref = {o["name"]: o for o in old}
            # alignment: the unscaled re-render must put each number where the published slot is
            d = [max(abs(o["x"] - r["x"]), abs(o["y"] - r["y"])) for r in s0 for o in [ref.get(r["name"])] if o]
            slots = []
            to_ij = grid_fn(m, M, ref, new)
            for nm, s_ in new.items():
                o = ref.get(nm)
                if o: slots.append(dict(o, x=s_["x"], y=s_["y"], size=s_["size"])); continue
                fi, fj = to_ij(s_["la"], s_["lo"])   # a town that now fits: its own grid point on this model
                slots.append(dict(name=nm, kind="town", x=s_["x"], y=s_["y"], fi=fi, fj=fj, size=s_["size"], color=s_["color"]))
            M["views"][vid]["towns"] = slots; M["views"][vid]["towns_png"] = png
            if vid == "pnwt" and m in fx.get("models", {}) and "pnwt" in fx["models"][m]: fx["models"][m]["pnwt"] = dict(towns=slots, towns_png=png)
            rep[f"{m}/{vid}"] = dict(old=len(old), new=len(slots), dropped=sorted(set(ref) - set(new)), max_unscaled_offset=round(max(d), 4) if d else None, matched=len(d))
    json.dump(man, open(f"{a.out}/manifest.json", "w")); json.dump(fx, open(f"{a.out}/view_fixes.json", "w"), indent=1)
    json.dump(rep, open(f"{a.out}/towns_report.json", "w"), indent=1); print(json.dumps(rep))
if __name__ == "__main__": main()
