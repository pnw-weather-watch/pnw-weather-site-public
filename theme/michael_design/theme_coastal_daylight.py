"""theme_coastal_daylight.py - "Coastal Daylight" site theme v1 + two sample products (Tue Nov 3, 2026 ~8:20 PM PST).
Original theme for the PNW / California / Hawaii site (see THEME_PROPOSAL.md). Not derived from Benjamin's current look:
sentence-case titles in Atkinson Hyperlegible (OFL), a left "time tile" instead of a corner forecast-hour tag, a vertical
rounded key on the RIGHT, H/L as filled discs, white land / sea-glass ocean.
Data: NOAA GFS 0.25 (public domain) via NOAA Open Data on AWS; basemap Natural Earth (public domain).
Run: python3 theme_coastal_daylight.py  -> mocks/theme_cd_t2m_pnw_v1.png, mocks/theme_cd_mslp_precip_pnw_v1.png"""
import os, datetime as dt, numpy as np, pygrib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import FancyBboxPatch
import cartopy.crs as ccrs, cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter, zoom, maximum_filter, minimum_filter
from zoneinfo import ZoneInfo
from h500_scale_build_v3 import path_cvd
HERE = os.path.dirname(os.path.abspath(__file__)); PT = ZoneInfo("America/Los_Angeles")
FD = "/usr/share/fonts/truetype/sand-box/google/Atkinson Hyperlegible/"
def F(w="r", s=14): return fm.FontProperties(fname=FD + ("AtkinsonHyperlegible-Bold.ttf" if w == "b" else "AtkinsonHyperlegible-Regular.ttf"), size=s)
# ---------------- theme tokens
T = dict(bg="#FFFFFF", land="#FFFFFF", ocean="#EAF4F4", lake="#EAF4F4", ink="#0B2545", muted="#5B6B7C", accent="#1F9E8F",
         coast="#7D8B99", border="#98A4AF", state="#B5BEC7", tile="#0B2545", tile_text="#FFFFFF", hi="#0B2545", lo="#E4572E",
         chip="#FFFFFF")
LW = dict(coast=1.5, country=1.2, state=0.85, isobar=1.6, isobar_halo=3.6, freeze=2.6, frame=0)
DPI = 100; W_IN = 21.0
# ---------------- scales (original)
# 2 m temperature: same family as temp850_scale (violet -> ice below 32 F, lemon -> wine above), wider range, 2 F bands
T2M_EDGES = list(range(-20, 111, 2))
T2M_COLORS = (["#1c0d33"] + path_cvd(["#2a1448", "#45237e", "#4a3fb4", "#3b6ad6", "#2f93dc", "#4fbad8", "#8fd8d6", "#d3eee6"], 26)
              + path_cvd(["#f1f3bf", "#f7e07a", "#f8b84c", "#f2843a", "#de4f2f", "#b7283a", "#7f1a3f", "#4e0f33"], 39) + ["#33091f"])
# 6 h precip (in): sea-glass -> lagoon blue -> indigo -> orchid -> coral -> gold (no green start), first band visible on white
QPF_EDGES = [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
QPF_COLORS = [None] + path_cvd(["#bfe9e4", "#5cc6c4", "#2a8fc0", "#3c58b4", "#6a3aa8", "#a8329a", "#dd4a6c", "#f6874a", "#fcc75a"], 13) + ["#fff0a8"]
def build(edges, colors):
    cm = ListedColormap(colors[1:-1]); cm.set_over(colors[-1]); cm.set_under(colors[0] or (0, 0, 0, 0))
    return cm, BoundaryNorm(edges, cm.N)
# ---------------- data
GRIB = os.path.join(HERE, "data", "gfs12z_20261103_f024_theme_v1.grb2")
g = pygrib.open(GRIB)
def get(name, extra=None):
    for m in g:
        if m.name == name or m.shortName == name:
            if extra is None or extra in str(m): g.rewind(); return m
    g.rewind(); raise KeyError(name)
mt = get("2t"); LAT, LON = mt.latlons(); T2 = (mt.values - 273.15) * 1.8 + 32
MSL = get("prmsl").values / 100.0; Q6 = get("tp", "18-24").values / 25.4
LAT = LAT[::-1, 0]; LON = LON[0]; T2 = T2[::-1]; MSL = MSL[::-1]; Q6 = Q6[::-1]
RUN = dt.datetime(2026, 11, 3, 12, tzinfo=dt.timezone.utc); FH = 24; VALID = RUN + dt.timedelta(hours=FH)
def sub(a, box):
    lo0, lo1, la0, la1 = box; j = (LON >= lo0 % 360) & (LON <= lo1 % 360); i = (LAT >= la0) & (LAT <= la1)
    return a[np.ix_(i, j)], LAT[i], LON[j] - 360
def up(z, la, lo, s=1.2, k=3): return zoom(gaussian_filter(z, s), k, order=3), np.linspace(la[0], la[-1], len(la) * k), np.linspace(lo[0], lo[-1], len(lo) * k)
def pt(t, f): return t.astimezone(PT).strftime(f)
PNW = dict(proj=ccrs.LambertConformal(central_longitude=-120.5, central_latitude=45.5, standard_parallels=(40, 50)),
           ext=[-130.5, -110.5, 40.3, 50.2], box=(-140, -100, 34, 56))
PNW_TOWNS = {"Seattle": (47.61, -122.33, "E"), "Portland": (45.52, -122.68, "E"), "Spokane": (47.66, -117.43, "E"),
             "Bellingham": (48.75, -122.48, "E"), "Yakima": (46.60, -120.51, "E"), "Eugene": (44.05, -123.09, "E"),
             "Bend": (44.06, -121.31, "E"), "Boise": (43.62, -116.20, "E"), "Medford": (42.33, -122.87, "E"),
             "Astoria": (46.19, -123.83, "E"), "Wenatchee": (47.42, -120.31, "E"), "Missoula": (46.87, -113.99, "E"),
             "Pendleton": (45.67, -118.79, "E"), "Victoria": (48.43, -123.37, "W"), "Kelowna": (49.89, -119.50, "E")}
# ---------------- layout
def frame(title, sub_txt, H_IN=14.0):
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI); fig.patch.set_facecolor(T["bg"])
    head, foot, keyw = 1.25, 0.45, 1.55                                   # inches
    ax = fig.add_axes([0.25 / W_IN, foot / H_IN, (W_IN - 0.25 - keyw) / W_IN, (H_IN - head - foot) / H_IN], projection=PNW["proj"])
    ax.set_extent(PNW["ext"], crs=ccrs.PlateCarree()); ax.set_facecolor(T["ocean"])
    ax.spines["geo"].set_visible(False)
    # time tile (left), then sentence-case title + run line
    tile = FancyBboxPatch((0.25 / W_IN, (H_IN - 1.08) / H_IN), 1.05 / W_IN, 0.9 / H_IN, boxstyle="round,pad=0,rounding_size=0.012",
                          transform=fig.transFigure, fc=T["tile"], ec="none"); fig.patches.append(tile)
    fig.text(0.775 / W_IN, (H_IN - 0.50) / H_IN, f"+{FH}h", fontproperties=F("b", 24), color=T["tile_text"], ha="center", va="center")
    fig.text(0.775 / W_IN, (H_IN - 0.86) / H_IN, pt(VALID, "%a %-I %p"), fontproperties=F("r", 12.5), color="#A9C6D9", ha="center", va="center")
    fig.text(1.55 / W_IN, (H_IN - 0.47) / H_IN, title, fontproperties=F("b", 30), color=T["ink"], va="center")
    fig.text(1.55 / W_IN, (H_IN - 0.90) / H_IN, sub_txt, fontproperties=F("r", 14.5), color=T["muted"], va="center")
    fig.text(1 - 0.25 / W_IN, (H_IN - 0.47) / H_IN, "Pacific Northwest", fontproperties=F("b", 16), color=T["accent"], ha="right", va="center")
    fig.text(1 - 0.25 / W_IN, (H_IN - 0.90) / H_IN, f"Valid {pt(VALID, '%a %b %-d, %-I:%M %p %Z')}", fontproperties=F("r", 14.5), color=T["ink"], ha="right", va="center")
    fig.add_artist(plt.Line2D([0.25 / W_IN, 1 - 0.25 / W_IN], [(H_IN - 1.2) / H_IN] * 2, transform=fig.transFigure, color=T["accent"], lw=2.5, solid_capstyle="round"))
    fig.text(0.25 / W_IN, 0.2 / H_IN, "Data: NOAA GFS 0.25° (public domain) · Basemap: Natural Earth", fontproperties=F("r", 12), color=T["muted"], va="center")
    fig.text(1 - 0.25 / W_IN, 0.2 / H_IN, "Times in Pacific Time · design mock · Coastal Daylight theme", fontproperties=F("r", 12), color=T["muted"], ha="right", va="center")
    return fig, ax, H_IN, head, foot, keyw
def basemap(ax, lakes_z=0.5):
    ax.add_feature(cfeature.LAND.with_scale("50m"), fc=T["land"], ec="none", zorder=0)
    ax.add_feature(cfeature.LAKES.with_scale("50m"), fc=T["lake"], ec="none", zorder=lakes_z)
    ax.add_feature(cfeature.LAKES.with_scale("50m"), fc="none", ec=T["coast"], lw=0.6, zorder=4)
    ax.add_feature(cfeature.STATES.with_scale("50m"), ec=T["state"], fc="none", lw=LW["state"], zorder=4)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), ec=T["border"], lw=LW["country"], zorder=4)
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), ec=T["coast"], lw=LW["coast"], zorder=4)
def vkey(fig, H_IN, head, foot, keyw, cmap, norm, edges, ticks, unit, fmt=lambda v: f"{v:g}", emph=None, ext="both"):
    """vertical key on the right: rounded capsule, labels right of it, unit on top"""
    x0 = (W_IN - keyw + 0.35) / W_IN; w = 0.34 / W_IN; y0 = (foot + 0.8) / H_IN; h = (H_IN - head - foot - 2.3) / H_IN
    kax = fig.add_axes([x0, y0, w, h]); kax.set_axis_off()
    n = len(edges) - 1; ys = np.linspace(0, 1, n + 1)
    for k in range(n): kax.add_patch(plt.Rectangle((0, ys[k]), 1, ys[k + 1] - ys[k], fc=cmap(k), ec="none"))
    capsule = FancyBboxPatch((0, -0.035), 1, 1.07, boxstyle="round,pad=0,rounding_size=0.5", transform=kax.transData, fc="none", ec=T["ink"], lw=1.2,
                             mutation_aspect=0.06)
    if ext in ("both", "min"): kax.add_patch(FancyBboxPatch((0, -0.035), 1, 0.05, boxstyle="round,pad=0,rounding_size=0.5", fc=cmap.get_under(), ec="none", mutation_aspect=0.06))
    kax.add_patch(FancyBboxPatch((0, 0.985), 1, 0.05, boxstyle="round,pad=0,rounding_size=0.5", fc=cmap.get_over(), ec="none", mutation_aspect=0.06))
    kax.add_patch(capsule); kax.set_xlim(0, 1); kax.set_ylim(-0.04, 1.04)
    pos = lambda v: np.interp(v, edges, ys)
    for t in ticks:
        kax.plot([1.0, 1.25], [pos(t)] * 2, color=T["ink"], lw=1.0, clip_on=False)
        kax.text(1.4, pos(t), fmt(t), fontproperties=F("b" if t == emph else "r", 14), color=T["accent"] if t == emph else T["ink"], va="center", clip_on=False)
    kax.text(0.5, 1.065, unit, fontproperties=F("b", 15), color=T["ink"], ha="center", va="bottom", clip_on=False)
def town_values(fig, ax, field, la, lo, fmt):
    from scipy.interpolate import RegularGridInterpolator
    it = RegularGridInterpolator((la, lo), gaussian_filter(field, 0.8))
    for name, (a, b, side) in PNW_TOWNS.items():
        v = float(it((a, b))); ax.plot(b, a, "o", ms=6, mfc=T["ink"], mec="white", mew=1.5, transform=ccrs.PlateCarree(), zorder=20)
        dx = 9 if side == "E" else -9
        ax.annotate(f"{name} {fmt(v)}", (b, a), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), xytext=(dx, 0), textcoords="offset points",
                    ha="left" if side == "E" else "right", va="center", fontproperties=F("b", 14), color=T["ink"], zorder=21,
                    bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.5", fc=(1, 1, 1, 0.82), ec="none"))
def hilo(ax, z, la, lo, size=28):
    zs = gaussian_filter(z, 3)
    for kind, f, col in (("H", maximum_filter, T["hi"]), ("L", minimum_filter, T["lo"])):
        mask = (zs == f(zs, size=size, mode="nearest"))
        for i, j in zip(*np.where(mask)):
            if i < 3 or j < 3 or i > len(la) - 4 or j > len(lo) - 4: continue
            a, b = la[i], lo[j]
            if not (PNW["ext"][0] + 0.6 < b < PNW["ext"][1] - 0.6 and PNW["ext"][2] + 0.5 < a < PNW["ext"][3] - 0.5): continue
            ax.plot(b, a, "o", ms=38, mfc=col, mec="white", mew=2.5, transform=ccrs.PlateCarree(), zorder=24)
            ax.text(b, a, kind, fontproperties=F("b", 22), color="white", ha="center", va="center", transform=ccrs.PlateCarree(), zorder=25)
            ax.annotate(f"{z[i, j]:.0f}", (b, a), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), xytext=(0, -30), textcoords="offset points",
                        ha="center", va="top", fontproperties=F("b", 14), color=col, zorder=25, path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])
def t2m():
    fig, ax, H, head, foot, keyw = frame("2 m temperature", f"GFS 0.25° · run {pt(RUN, '%a %-I %p %Z')} ({RUN:%HZ}) · bold line = 32°F")
    basemap(ax, lakes_z=3); z, la, lo = sub(T2, PNW["box"]); zf, laf, lof = up(z, la, lo, 0.8)
    cm, nm = build(T2M_EDGES, T2M_COLORS)
    cf = ax.contourf(lof, laf, zf, levels=T2M_EDGES, cmap=cm, norm=nm, extend="both", transform=ccrs.PlateCarree(), zorder=1)
    cf.set_edgecolor("face")
    cs = ax.contour(lof, laf, zf, levels=[32], colors=[T["ink"]], linewidths=LW["freeze"], transform=ccrs.PlateCarree(), zorder=6)
    cs.set(path_effects=[pe.withStroke(linewidth=4.6, foreground="white", alpha=0.8)])
    town_values(fig, ax, z, la, lo, lambda v: f"{v:.0f}°")
    vkey(fig, H, head, foot, keyw, cm, nm, T2M_EDGES, [-20, 0, 20, 32, 50, 70, 90, 110], "°F", emph=32)
    out = os.path.join(HERE, "mocks", "theme_cd_t2m_pnw_v1.png"); fig.savefig(out, dpi=DPI); plt.close(fig); return out
def mslp_precip():
    fig, ax, H, head, foot, keyw = frame("Pressure + 6 h precipitation", f"GFS 0.25° · run {pt(RUN, '%a %-I %p %Z')} ({RUN:%HZ}) · precip in the 6 h ending at valid time · isobars every 4 mb")
    basemap(ax, lakes_z=0.5); q, la, lo = sub(Q6, PNW["box"]); qf, laf, lof = up(q, la, lo, 0.9)
    cm, nm = build(QPF_EDGES, QPF_COLORS)
    ax.contourf(lof, laf, qf, levels=QPF_EDGES, cmap=cm, norm=nm, extend="max", transform=ccrs.PlateCarree(), zorder=1)
    p, pla, plo = sub(MSL, PNW["box"]); pf, plaf, plof = up(p, pla, plo, 2.0)
    lev = np.arange(960, 1060, 4)
    cs = ax.contour(plof, plaf, pf, levels=lev, colors=[T["ink"]], linewidths=LW["isobar"], transform=ccrs.PlateCarree(), zorder=7)
    cs.set(path_effects=[pe.withStroke(linewidth=LW["isobar_halo"], foreground="white", alpha=0.85)])
    lab = ax.clabel(cs, fmt="%d", inline=True, inline_spacing=8)
    for t in lab: t.set_fontproperties(F("b", 12.5)); t.set_color(T["ink"])
    hilo(ax, p, pla, plo)
    for name, (a, b, side) in PNW_TOWNS.items():
        ax.plot(b, a, "o", ms=6, mfc=T["ink"], mec="white", mew=1.5, transform=ccrs.PlateCarree(), zorder=20)
        ax.annotate(name, (b, a), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), xytext=(9 if side == "E" else -9, 0), textcoords="offset points",
                    ha="left" if side == "E" else "right", va="center", fontproperties=F("r", 13.5), color=T["ink"], zorder=21,
                    path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    vkey(fig, H, head, foot, keyw, cm, nm, QPF_EDGES, [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0], "in", ext="max")
    out = os.path.join(HERE, "mocks", "theme_cd_mslp_precip_pnw_v1.png"); fig.savefig(out, dpi=DPI); plt.close(fig); return out
if __name__ == "__main__":
    print(t2m()); print(mslp_precip())
    print("T2 range in view", float(np.nanmin(sub(T2, PNW["box"])[0])), float(np.nanmax(sub(T2, PNW["box"])[0])), "Q6 max", float(sub(Q6, PNW["box"])[0].max()))
