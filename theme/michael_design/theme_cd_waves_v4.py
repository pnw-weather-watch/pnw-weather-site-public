"""theme_cd_waves_v4.py - v4 (Tue Nov 3, 2026 ~10:10 PM PST): Benjamin t80u/t81u "keep the base map white, but the empty space
around the image black": light warm off-white land inside the map, near-black #05080d canvas/header/footer/key surround,
borders re-picked for the light land. Everything else = night v3 (36 bands, Mercator, corner text, small arrows).
v3 header: theme_cd_waves_v3.py - night v3 (Tue Nov 3, 2026 ~10:00 PM PST): Benjamin t77u "a little too smooth" -> 2x the 18 base bands
(36 per scale; WAVE_K env var = split factor, default 2). Same anchors/nudges/layout as night v2. Outputs *_night_v3.png.
v2 header: theme_cd_waves_v2.py - v2 (Tue Nov 3, 2026 ~9:55 PM PST): Mercator views so the West Coast runs near-vertical and the frame is upright
(v1 used Lambert with central meridian -145, which rotated the coast); Hs band 6-8 ft nudged #3e69ac -> #32599e (tritan pass).
3x bands (54 per scale, OKLab). NIGHT MODE canvas. Outputs *_night_v2.png. v1 header: theme_cd_waves_v1.py - Coastal Daylight theme v1 mocks: estimated max wave height + significant wave height & direction
(Tue Nov 3, 2026 ~9:45 PM PST). Data: ECMWF IFS HRES-WAM 0.25 open data (CC BY 4.0 + ECMWF Terms of Use), 12Z Nov 3 2026 run,
step 276 h (valid 00Z Sun Nov 15 = Sat Nov 14 4 PM PST), fields swh, mwd, pp1d. The open set has no maximum individual wave
height (hmax) field, so max wave = 1.86 x swh (Rayleigh: expected largest of ~1000 waves ~ 1.86 Hs) - stated in the footnote.
Original palettes (own anchors, path_cvd spacing); not Benjamin's ramp/breakpoints. Light theme variant (white land).
Outputs: mocks/theme_cd_wave_max_nepac_v1.png, mocks/theme_cd_wave_hs_dir_nepac_v1.png, mocks/theme_cd_wave_hs_dir_pnw_v4.png" if K == 2 else f"_v4_k{K}_tmp.png"""
import os, datetime as dt, numpy as np, pygrib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
import cartopy.crs as ccrs, cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter, zoom
import theme_coastal_daylight as TH, qa_cvd as Q
from h500_scale_build_v3 import path_cvd
F, T, LW, PT, HERE, DPI, W_IN = TH.F, TH.T, TH.LW, TH.PT, TH.HERE, TH.DPI, TH.W_IN
# ---- NIGHT MODE (Benjamin t75u): dark navy canvas, light text, slate land; mutates the theme tokens for this script only
NAVY = "#05080d"          # v4: near-black page surround (name kept)
T.update(bg=NAVY, ink="#E8F0F7", muted="#9FB3C8", accent="#3CC8B4", tile=NAVY, coast="#9AAEC2", border="#71839A", state="#56677B",
         land="#F6F4EF", ocean="#DDEBF0", hi="#E8F0F7", coast_land="#4E5D6E")
CHIP = (0.04, 0.09, 0.15, 0.82)
PC = ccrs.PlateCarree(); M2FT = 3.28084; HMAX_FACTOR = 1.86
# ---------- data
g = pygrib.open(os.path.join(HERE, "data", "ecmwf_wave_2026110312z_f276.grib2"))
def fld(n):
    m = [x for x in g if x.shortName == n][0]; g.rewind(); return m
m = fld("swh"); la2, lo2 = m.latlons(); LAT = la2[::-1, 0]; LON = lo2[0]
_ORD = np.argsort(LON % 360)                    # 0..360 grid: the Pacific is continuous (no dateline seam)
LON = (LON % 360)[_ORD]
def arr(n): v = fld(n).values; return np.ma.filled(v, np.nan)[::-1][:, _ORD]
HS = arr("swh") * M2FT; MWD = arr("mwd"); PP = arr("pp1d")
RUN = dt.datetime(2026, 11, 3, 12, tzinfo=dt.timezone.utc); FH = 276; VALID = RUN + dt.timedelta(hours=FH)
assert fld("swh").validDate == VALID.replace(tzinfo=None)
def pt(t, f): return t.astimezone(PT).strftime(f)
# ---------- scales (original)
MAX_EDGES = [0, 3, 6, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]
MAX_ANCHORS = ["#dff1f4", "#9fd9e6", "#4fb3d6", "#2e7fc4", "#3a55b0", "#2f9e9a", "#a6c94a", "#f2cf3e", "#f59a36",
               "#e2553a", "#c22a5a", "#8f2380", "#5b2690", "#d36fd6", "#ffc2ec"]
MAX_COLORS = path_cvd(MAX_ANCHORS, 18); MAX_COLORS = [MAX_COLORS[0]] + MAX_COLORS + ["#fff0fa"]       # under(unused) + 18 + over
HS_EDGES = [0, 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 23, 26, 30, 35, 40, 50]
HS_ANCHORS = ["#e6f4f6", "#a8dbe6", "#5bb7d6", "#2f84c5", "#3c5ab1", "#2a9c98", "#9cc64c", "#efcd42", "#f49a39",
              "#df553b", "#be2b5c", "#86257f", "#4f2786"]
HS_COLORS = path_cvd(HS_ANCHORS, 18); HS_COLORS = [HS_COLORS[0]] + HS_COLORS + ["#c993d9"]
def build(edges, colors):
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cm = ListedColormap(colors[1:-1]); cm.set_over(colors[-1]); cm.set_under(colors[0]); return cm, BoundaryNorm(edges, cm.N)
HS_COLORS[6] = "#00407a"                       # v2 nudge (was #3e69ac; #32599e fixed base bands but not the 3x every-3rd check)
HS_COLORS[11] = "#d3e550"                      # v2 nudge (was #edcd42) for deutan every-3rd
MAX_COLORS[5] = "#545d90"                      # v2 nudge (was #3f69ab) for tritan every-3rd
# v2 (Benjamin t73u/t74u): 3x smoother bands. Each band split into 3 (linear in value); fine band 3k = old band k exactly and
# the next two step toward band k+1 in OKLab (the last band steps toward the 'over' colour). Ticks stay at the round values.
import anom_scale as _A
MAX_BASE, HS_BASE = list(MAX_COLORS), list(HS_COLORS)
def triple(edges, colors, k=3):
    body = colors[1:-1] + [colors[-1]]; out = []
    for i in range(len(edges) - 1):
        a, b = _A._to_ok(body[i]), _A._to_ok(body[i + 1])
        for t in range(k): out.append(_A._from_ok(a + (b - a) * t / k))
    e = []
    for i in range(len(edges) - 1):
        for t in range(k): e.append(round(edges[i] + (edges[i + 1] - edges[i]) * t / k, 4))
    return e + [edges[-1]], [colors[0]] + out + [colors[-1]]
K = int(os.environ.get("WAVE_K", "2"))
MAX_EDGES, MAX_COLORS = triple(MAX_EDGES, MAX_COLORS, K)
HS_EDGES, HS_COLORS = triple(HS_EDGES, HS_COLORS, K)
VIEWS = {"nepac": dict(proj=ccrs.Mercator(central_longitude=-140),
                       ext=[-184, -108, 14, 62.5], name="Northeast Pacific", step=2.1, h=17.2),
         "pnw": dict(proj=ccrs.Mercator(central_longitude=-127),
                     ext=[-145, -116, 38.5, 51.5], name="Pacific Northwest coast", step=0.68, h=13.6)}
TOWNS = {"nepac": {"Seattle": (47.61, -122.33, "E"), "Portland": (45.52, -122.68, "E"), "San Francisco": (37.77, -122.42, "E"),
                   "Los Angeles": (34.05, -118.24, "E"), "Honolulu": (21.31, -157.86, "E"), "Anchorage": (61.22, -149.90, "E"),
                   "Juneau": (58.30, -134.42, "E")},
         "pnw": {"Seattle": (47.61, -122.33, "E"), "Portland": (45.52, -122.68, "E"), "Astoria": (46.19, -123.83, "E"),
                 "Newport": (44.64, -124.05, "E"), "Coos Bay": (43.37, -124.22, "E"), "Eureka": (40.80, -124.16, "E"),
                 "Westport": (46.89, -124.10, "E"), "Neah Bay": (48.37, -124.62, "E")}}
CREDIT1 = "Based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF), modified (unit conversion, derived max wave, display binning) · © 2026 ECMWF · ecmwf.int · CC BY 4.0 creativecommons.org/licenses/by/4.0"
CREDIT2 = "ECMWF does not accept any liability whatsoever for any error or omission in the data, their availability, or for any loss or damage arising from their use. · Basemap: Natural Earth · Times in Pacific Time · theme v1 mock · v4"
def frame(v, title, sub_txt):
    H_IN = v["h"]; fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI); fig.patch.set_facecolor(T["bg"])
    head, foot, keyw = 1.25, 0.95, 1.55
    ax = fig.add_axes([0.25 / W_IN, foot / H_IN, (W_IN - 0.25 - keyw) / W_IN, (H_IN - head - foot) / H_IN], projection=v["proj"])
    ax.set_extent(v["ext"], crs=PC); ax.set_facecolor(T["ocean"]); fig.patch.set_facecolor(NAVY); ax.spines["geo"].set_visible(False)
    fig.patches.append(FancyBboxPatch((0.25 / W_IN, (H_IN - 1.08) / H_IN), 1.05 / W_IN, 0.9 / H_IN, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, fc=T["tile"], ec=T["accent"], lw=2.2))
    fig.text(0.775 / W_IN, (H_IN - 0.50) / H_IN, f"+{FH}h", fontproperties=F("b", 22), color="white", ha="center", va="center")
    fig.text(0.775 / W_IN, (H_IN - 0.86) / H_IN, pt(VALID, "%a %-I %p"), fontproperties=F("r", 12.5), color="#A9C6D9", ha="center", va="center")
    fig.text(1.55 / W_IN, (H_IN - 0.47) / H_IN, title, fontproperties=F("b", 30), color=T["ink"], va="center")
    fig.text(1.55 / W_IN, (H_IN - 0.90) / H_IN, sub_txt, fontproperties=F("r", 14.5), color=T["muted"], va="center")
    fig.text(1 - 0.25 / W_IN, (H_IN - 0.47) / H_IN, v["name"], fontproperties=F("b", 16), color=T["accent"], ha="right", va="center")
    fig.text(1 - 0.25 / W_IN, (H_IN - 0.90) / H_IN, f"Valid {pt(VALID, '%a %b %-d, %-I:%M %p %Z')}", fontproperties=F("r", 14.5), color=T["ink"], ha="right", va="center")
    fig.add_artist(plt.Line2D([0.25 / W_IN, 1 - 0.25 / W_IN], [(H_IN - 1.2) / H_IN] * 2, transform=fig.transFigure, color=T["accent"], lw=2.5, solid_capstyle="round"))
    fig.text(0.25 / W_IN, 0.62 / H_IN, CREDIT1, fontproperties=F("r", 11), color=T["muted"], va="center")
    fig.text(0.25 / W_IN, 0.36 / H_IN, CREDIT2, fontproperties=F("r", 11), color=T["muted"], va="center")
    return fig, ax, H_IN, head, foot, keyw
def basemap(ax):
    ax.add_feature(cfeature.LAND.with_scale("50m"), fc=T["land"], ec="none", zorder=5)        # v4: light warm off-white land
    ax.add_feature(cfeature.LAKES.with_scale("50m"), fc=T["ocean"], ec=T["coast"], lw=0.5, zorder=5.1)
    ax.add_feature(cfeature.STATES.with_scale("50m"), ec="#7f8da0", fc="none", lw=1.7, zorder=5.2)          # t82u: ~2x, mid-slate
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), ec="#5b6b7d", lw=2.4, zorder=5.25)              # t82u: ~2x, lighter slate
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), ec=T["coast_land"], lw=LW["coast"], zorder=5.3)
def sea_fill(ax, z, edges, colors, ext="max"):
    zf = zoom(np.nan_to_num(gaussian_filter(np.nan_to_num(z, nan=0), 0.8), nan=0), 2, order=1)
    laf = np.linspace(LAT[0], LAT[-1], len(LAT) * 2); lof = np.linspace(LON[0], LON[-1], len(LON) * 2)
    cm, nm = build(edges, colors)
    cf = ax.contourf(lof, laf, zf, levels=edges, cmap=cm, norm=nm, extend=ext, transform=PC, zorder=1); cf.set_edgecolor("face")
    return cm, nm
def towns(ax, v):
    for name, (a, b, side) in TOWNS[v].items():
        ax.plot(b, a, "o", ms=6, mfc=T["ink"], mec=NAVY, mew=1.5, transform=PC, zorder=20)
        ax.annotate(name, (b, a), xycoords=PC._as_mpl_transform(ax), xytext=(8, 0), textcoords="offset points", ha="left", va="center",
                    fontproperties=F("b", 13.5), color=T["ink"], zorder=21, bbox=dict(boxstyle="round,pad=0.2,rounding_size=0.5", fc=CHIP, ec="none"))
def peak_labels(ax, z, v, cm, nm, n=10):
    """value chips at the largest local maxima in view (no buoy data used)"""
    from scipy.ndimage import maximum_filter
    zs = np.nan_to_num(gaussian_filter(np.nan_to_num(z), 1.0)); mx = (zs == maximum_filter(zs, size=40)) & (zs > 25)
    lo0, lo1, la0, la1 = v["ext"]; pts = [(zs[i, j], LAT[i], LON[j]) for i, j in zip(*np.where(mx)) if la0 + 1 < LAT[i] < la1 - 1 and (lo0 % 360) + 1 < LON[j] < (lo1 % 360) - 1]
    for val, a, b in sorted(pts, reverse=True)[:n]:
        ax.text(b, a, f"{val:.0f}", transform=PC, fontproperties=F("b", 15), color=T["ink"], ha="center", va="center", zorder=22,
                bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.6", fc=NAVY, ec=T["accent"], lw=1.4))
def arrows(ax, v, cm, nm, edges):
    s = v["step"]; lo0, lo1, la0, la1 = v["ext"]
    la_s = np.arange(la0 + s / 2, la1, s); xs, ys, us, vs, cols = [], [], [], [], []
    for a in la_s:
        ds = s / max(np.cos(np.radians(a)), 0.3)
        for b in np.arange(lo0 + ds / 2, lo1, ds):
            i = int(round((a - LAT[0]) / (LAT[1] - LAT[0]))); j = int(round(((b % 360) - LON[0]) / (LON[1] - LON[0]))) % len(LON)
            if np.isnan(HS[i, j]) or np.isnan(MWD[i, j]): continue
            d = np.radians((MWD[i, j] + 180) % 360)              # mwd = direction waves come FROM (deg true); draw toward
            xs.append(b); ys.append(a); us.append(np.sin(d)); vs.append(np.cos(d))
            L = Q.lab(Q.lin(np.array([cm(nm(HS[i, j]))[:3]])))[0][0]; cols.append("white" if L < 48 else NAVY)
    xs, ys, us, vs = map(np.array, (xs, ys, us, vs))
    # rotate unit vectors into the projection
    P0 = ax.projection.transform_points(PC, xs, ys); e = 0.05
    P1 = ax.projection.transform_points(PC, xs + e * us / np.cos(np.radians(ys)), ys + e * vs)
    dx, dy = P1[:, 0] - P0[:, 0], P1[:, 1] - P0[:, 1]; n = np.hypot(dx, dy); dx, dy = dx / n, dy / n
    for c in ("white", NAVY):
        k = np.array([x == c for x in cols])
        if k.any():
            ax.quiver(P0[k, 0], P0[k, 1], dx[k], dy[k], transform=ax.projection, color=c, scale=77, width=0.0015, headwidth=3.4, headlength=3.7,
                      headaxislength=3.2, pivot="middle", zorder=9,
                      path_effects=[pe.withStroke(linewidth=1.9, foreground=(NAVY if c == "white" else "white"), alpha=0.65)])
    return len(xs)
def wave_max(v="nepac"):
    V = VIEWS[v]; fig, ax, H, head, foot, keyw = frame(V, "Estimated maximum wave height",
        f"ECMWF IFS HRES-WAM 0.25° · run {pt(RUN, '%a %b %-d %-I %p %Z')} ({RUN:%HZ}) · max wave ≈ 1.86 × significant height (no max-wave field in open data)")
    z = HS * HMAX_FACTOR; cm, nm = sea_fill(ax, z, MAX_EDGES, MAX_COLORS); basemap(ax); towns(ax, v)
    # Benjamin t76u: no in-map value chips; plain text bottom-right with the max in view
    lo0, lo1, la0, la1 = V["ext"]; jj = ((LON >= lo0 % 360) & (LON <= lo1 % 360)) if lo0 % 360 < lo1 % 360 else ((LON >= lo0 % 360) | (LON <= lo1 % 360))
    vmax = float(np.nanmax(z[np.ix_((LAT >= la0) & (LAT <= la1), jj)]))
    # Benjamin t78u: inside the map, bottom-right, ~3.5% above the map's bottom edge; bigger/bolder, white with soft dark shadow
    ax.text(0.985, 0.035, f"Maximum wave height: {vmax:.0f} ft", transform=ax.transAxes, fontproperties=F("b", 29), color="white",
            ha="right", va="bottom", zorder=30,
            path_effects=[pe.withStroke(linewidth=6, foreground=(0.02, 0.05, 0.1, 0.30)),
                          pe.SimplePatchShadow(offset=(2.5, -2.5), shadow_rgbFace=(0.02, 0.05, 0.1), alpha=0.65), pe.Normal()])
    TH.vkey(fig, H, head, foot, keyw, cm, nm, MAX_EDGES, [0, 10, 20, 30, 40, 50, 60, 70, 85], "ft", ext="max")
    out = os.path.join(HERE, "mocks", f"theme_cd_wave_max_{v}_v4.png" if K == 2 else f"_v4_k{K}_tmp.png"); fig.savefig(out, dpi=DPI, facecolor=NAVY); plt.close(fig); return out, float(np.nanmax(z))
def wave_hs(v="nepac"):
    V = VIEWS[v]; fig, ax, H, head, foot, keyw = frame(V, "Significant wave height + wave direction",
        f"ECMWF IFS HRES-WAM 0.25° · run {pt(RUN, '%a %b %-d %-I %p %Z')} ({RUN:%HZ}) · arrows = mean wave direction (toward) · dashed = peak period 14 / 18 s")
    cm, nm = sea_fill(ax, HS, HS_EDGES, HS_COLORS); basemap(ax)
    pps = gaussian_filter(np.nan_to_num(PP, nan=0), 1.5)
    cs = ax.contour(LON, LAT, np.where(np.isnan(PP), np.nan, pps), levels=[14, 18], colors=[NAVY], linewidths=1.6, linestyles=[(0, (5, 3))], transform=PC, zorder=7)
    for t in ax.clabel(cs, fmt="%d s", inline=True, inline_spacing=6):
        t.set_fontproperties(F("b", 12.5)); t.set_color(T["ink"]); t.set_bbox(dict(boxstyle="round,pad=0.15,rounding_size=0.4", fc=NAVY, ec="none", alpha=0.85))
    n = arrows(ax, V, cm, nm, HS_EDGES); towns(ax, v)
    TH.vkey(fig, H, head, foot, keyw, cm, nm, HS_EDGES, [0, 2, 4, 8, 12, 16, 20, 30, 40, 50], "ft", ext="max")
    out = os.path.join(HERE, "mocks", f"theme_cd_wave_hs_dir_{v}_v4.png" if K == 2 else f"_v4_k{K}_tmp.png"); fig.savefig(out, dpi=DPI, facecolor=NAVY); plt.close(fig); return out, n
def qa():
    lines = ["Wave scales v2 CVD QA (CIE76, Machado 2009; strict neighbour line 5)"]
    for name, c in ((f"max_wave 0-85 ft ({18*K} bands)", MAX_COLORS[1:-1]), (f"hs 0-50 ft ({18*K} bands)", HS_COLORS[1:-1])):
        for k, mm in Q.M.items():
            L = Q.sim_lab(c, mm); d = np.linalg.norm(np.diff(L, axis=0), axis=1); d3 = np.linalg.norm(L[3:] - L[:-3], axis=1); dk = np.linalg.norm(L[K:] - L[:-K], axis=1)
            lines.append(f"{name:28s} {k:7s} neighbour min={d.min():4.1f} mean={d.mean():4.1f} ({'strict pass' if d.min() >= 5 else 'below strict 5, expected for a gradient'})  "
                         f"every-3rd min={d3.min():4.1f} {'pass' if d3.min() >= 5 else 'LOW'}  every-{K}nd (=1 base step) min={dk.min():4.1f} {'pass' if dk.min() >= 5 else 'LOW'}")
    for name, c in (("max_wave base 18", MAX_BASE[1:-1]), ("hs base 18 (nudged)", HS_BASE[1:-1])):
        for k, mm in Q.M.items():
            L = Q.sim_lab(c, mm); d = np.linalg.norm(np.diff(L, axis=0), axis=1)
            lines.append(f"{name:28s} {k:7s} base-band neighbour min={d.min():4.1f} {'pass' if d.min() >= 5 else 'LOW'}")
    for name, c in (("max_wave", MAX_COLORS[1:-1]), ("hs", HS_COLORS[1:-1])):
        for k, mm in Q.M.items():
            L = Q.sim_lab([T["land"]] + c, mm); dl = min(np.linalg.norm(L[0] - x) for x in L[1:])
            lines.append(f"{name:28s} {k:7s} v4: closest scale colour to light land {T['land']} dE={dl:4.1f}")
    open(os.path.join(HERE, "qa_cvd_wave_scales_v4.txt"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
if __name__ == "__main__" and K != 2:
    print(wave_max("nepac")); raise SystemExit
if __name__ == "__main__":
    qa(); print(MAX_COLORS); print(HS_COLORS)
    print(wave_max("nepac")); print(wave_hs("nepac")); print(wave_hs("pnw"))
