#!/usr/bin/env python3
"""Per-view town-layer fixes the VIEWER uses (static/view_fixes.json): town names + number slots for the Pacific NW tight
view. Extracted from Benjamin's studio_views.py (pnwt_fix + town_slots only); the Studio-only wide view code is not included.
  view_fixes.py --manifest data/manifest.json --out D --models gfs,ifs
"""
import os, sys, json, argparse, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fast_encode as FE
FIX_VID, FIX_PNG = "pnwt", "static/towns_pnwt_v2_gs.png"   # 11-08: _gs = smaller global-model names (house_style.town_scale)

def town_slots(TM, vid, layer_fig, i0, i1, j0, j1, rs_, passes=False):
    """Town names + number slots for a view on a lat/lon model crop (same code as fast_encode.static): the site's own placement
    (temp_maps.towns) with "88" numbers; each number reads the grid point found by sampling lat and lon grids at the pins.
    Returns (figure with the names / dots, numbers hidden: the town layer), slots."""
    import numpy as np, matplotlib.pyplot as plt
    crop_la = 90.0 - np.arange(i0, i1) * rs_; crop_lo = np.mod(np.arange(j0, j1) * rs_, 360.0)
    wcols = np.where(crop_lo >= 180)[0]; tw_lo1 = crop_lo[wcols] - 360; tw_la1 = crop_la
    tw_la, tw_lo = np.meshgrid(tw_la1, tw_lo1, indexing="ij")
    f88 = lambda v: None if not np.isfinite(v) else "88"
    fig, ax, ky = layer_fig(); arts = TM.towns(ax, vid, (tw_la1, tw_lo1, tw_la), f88) or []
    tv_la = dict(getattr(ax, "town_values", {}) or {})
    fig2, ax2, _ = layer_fig(); TM.towns(ax2, vid, (tw_la1, tw_lo1, tw_lo), f88); tv_lo = dict(getattr(ax2, "town_values", {}) or {}); plt.close(fig2)
    fig.canvas.draw(); r = fig.canvas.get_renderer(); Wd, Hd = fig.get_size_inches() * fig.dpi; slots = []; last = None
    for t in arts:
        if t.get_text() != "88": last = t.get_text(); continue
        if not t.get_visible() or last not in tv_la: continue
        pla, plo = tv_la[last], tv_lo.get(last)
        if plo is None or not (np.isfinite(pla) and np.isfinite(plo)): continue
        bb = t.get_window_extent(r)
        slots.append(dict(name=last, kind="town", x=bb.x0 / Wd, y=1 - (bb.y0 + bb.y1) / 2 / Hd, fi=float((90.0 - pla) / rs_ - i0),
                          fj=float(np.mod(plo, 360.0) / rs_ - j0), size=t.get_fontsize(), color=t.get_color()))
        t.set_visible(False)
    return fig, slots

def pnwt_fix(models, man, out):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt, cartopy.crs as ccrs
    import house_style as HS, temp_maps as TM
    HS.use_for_plots(); FE.extra_views(TM, ccrs)
    os.makedirs(f"{out}/static/x2", exist_ok=True)
    def layer_fig():
        fig, ax, ky = TM.frame(FIX_VID); fig.set_dpi(FE.DPI); fig.patch.set_alpha(0); ax.patch.set_alpha(0); return fig, ax, ky
    fp = f"{out}/static/view_fixes.json"; doc = json.load(open(fp)) if os.path.exists(fp) else {"models": {}}
    names0 = None
    for m in models:
        MD = FE.MODELS[m]
        if m not in man.get("models", {}) or FIX_VID not in man["models"][m]["views"]: print(f"{m}: no {FIX_VID} view, skipped", flush=True); continue
        i0, i1, j0, j1 = man["models"][m]["crop"]
        with HS.town_scale(m, FIX_VID): fig, slots = town_slots(TM, FIX_VID, layer_fig, i0, i1, j0, j1, MD.get("res", 0.25))
        names = [s_["name"] for s_ in slots]
        if names0 is None:
            fig.savefig(f"{out}/{FIX_PNG}", dpi=FE.DPI, transparent=True); fig.savefig(f"{out}/{FIX_PNG}".replace("/static/", "/static/x2/"), dpi=FE.DPI * FE.X2, transparent=True)
            names0 = names
        elif names != names0: raise SystemExit(f"{m}: town placement differs from the shared towns layer")
        plt.close(fig)
        doc["models"].setdefault(m, {})[FIX_VID] = dict(towns=slots, towns_png=FIX_PNG)
        print(f"{m} {FIX_VID}: {len(slots)} town numbers", flush=True)
    doc.update(built=time.strftime("%Y-%m-%dT%H:%M:%S%z"), note="per-view overrides the site lays over manifest.json (view_fixes.py)")
    json.dump(doc, open(fp, "w"), indent=1); print("towns", names0, flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--models", default="gfs,ifs,ifs9,aifs,eps,aens"); a = ap.parse_args()
    pnwt_fix(a.models.split(","), json.load(open(a.manifest)), a.out)
