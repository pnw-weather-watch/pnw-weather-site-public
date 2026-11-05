"""THEME LAYER for the map renderers (Python side). house_style.py and menu_maps.py call apply_*() at import end, so every
palette, font, key size and marker color below replaces Benjamin's values without touching drawing logic.
Values: Michael Weather Bot's "Coastal Daylight" theme (design/THEME_PROPOSAL.md v1) + his scales (anom v6, snow v6,
temp850 v1, QPF, waves v4). Change looks here or in theme/*.json only."""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TD = os.environ.get("WX_THEME_DIR", os.path.normpath(os.path.join(HERE, "..", "..", "theme")))
FONTS = os.environ.get("WX_THEME_FONTS", os.path.normpath(os.path.join(HERE, "..", "fast", "site", "fonts")))
J = lambda n: json.load(open(os.path.join(TD, n)))
T = J("theme.json"); MAP = T["map"]

def apply_house_style(g):
    """g = house_style globals()."""
    from matplotlib import font_manager
    sm = g["smooth"]
    # page / header / key chrome on rendered PNGs (header layout itself is house_style.header + the viewer's header())
    g.update(BG=MAP["bg"], PANEL_EDGE=MAP["panel_edge"], INK=MAP["ink"], MUTED=MAP["muted"], ACCENT=MAP["accent"], BADGE=MAP["badge"],
             COAST_DARK=MAP["coast"], H_COLOR=MAP["hi"], L_COLOR=MAP["lo"], BAR_LABEL_SIZE=T["key"]["label_size"])
    # map line widths (Benjamin 11-3: thicker state and country lines); country never thinner than state
    Ln = T.get("lines", {})
    if Ln: g.update(COAST_LW=Ln["coast"], STATE_LW=Ln["state"], COUNTRY_LW=max(Ln["country"], Ln["state"]), ISOBAR_LW=Ln["isobar"], ISOBAR_HALO=Ln["isobar_halo"])
    # font: static Atkinson Hyperlegible (regular < 600 <= bold); replaces the variable-Montserrat instancer
    fp = {}
    def font(weight=500, size=12):
        path = os.path.join(FONTS, "atkinson-hyperlegible-700.ttf" if weight >= 600 else "atkinson-hyperlegible-regular.ttf")
        if path not in fp: font_manager.fontManager.addfont(path); fp[path] = 1
        return font_manager.FontProperties(fname=path, size=size)
    def use_for_plots():
        import matplotlib as mpl
        mpl.rcParams["font.family"] = font(500).get_name()
    g.update(font=font, use_for_plots=use_for_plots, _fp={500: os.path.join(FONTS, "atkinson-hyperlegible-regular.ttf"), 700: os.path.join(FONTS, "atkinson-hyperlegible-700.ttf")})
    # 500 mb height anomaly: Michael anom_scale v6 (white near normal, grey / grey-purple extremes)
    A = J("michael_design/anom_scale.json")["products"]["h500_anom"]
    E = np.array(A["edges"]); C = A["colors"]
    g.update(ANOM_LEVELS=E, ANOM_COLORS=C[1:-1], ANOM_UNDER=C[0], ANOM_OVER=C[-1], ANOM_TICKS=A["ticks"])
    mids = (E[:-1] + E[1:]) / 2.0
    def _anom_color(m):   # used by t850a (27x) and the SLP anomaly palettes
        return C[1:-1][int(np.clip(np.searchsorted(E, m) - 1, 0, len(C) - 3))]
    g["_anom_color"] = _anom_color
    # temperature: Michael temp850 v1 (-40..80 F, 2 F); 80..120 F extended to wine/orchid (KIT ADDITION, confirm with Michael)
    TS = J("temp_scale.json"); te = TS["edges_F"]; tc = TS["colors"]
    tmids = [(a + b) / 2 for a, b in zip(te[:-1], te[1:])]
    hot = [80, 86, 95, 105, 120]; hotc = ["#5c0f3a", "#7a1f66", "#9c3f94", "#c06fc0", "#f6d6f3"]   # [MICHAEL 11-3 fix] old start repeated the 78-80 F wine (no step at 80 F)
    def temp_color(f):
        if f < te[0]: return tc[0]
        if f <= te[-1]: return tc[1:-1][min(len(tc) - 3, int((f - te[0]) // 2))]
        return sm([f], hot, hotc)[0]
    L = g["TEMP_LEVELS"]; g["temp_color"] = temp_color
    g["TEMP_COLORS"] = [temp_color(v) for v in (L[:-1] + L[1:]) / 2.0]
    g["TEMP_UNDER"], g["TEMP_OVER"] = tc[0], tc[-1]   # 11-05: under/over from theme/temp_scale.json (all models share)
    L8 = g["T850_LEVELS"]; g["T850_COLORS"] = [temp_color(c * 1.8 + 32) for c in (L8[:-1] + L8[1:]) / 2.0]
    # precip (6 h / totals): Michael QPF ramp (no green); RAIN_* keeps Benjamin's level spacing, colors re-mapped onto Michael's edges
    Q = J("qpf_wave_scales.json")["qpf"]; qe = Q["edges_in"]; qc = Q["colors"]
    def rain_color(v):   # 3..12 in: Michael's ramp stops at 3 in; extended gold -> amber -> umber (KIT ADDITION, confirm with Michael)
        if v >= qe[-1]: return sm([v], [3.0, 5.0, 8.0, 12.0], ["#ec9440", "#cc6a2a", "#9c4320", "#5c2414"])[0]   # [MICHAEL 11-3 fix] old start went near-white pale yellow above 3 in (vanished on the white base)
        return qc[1:-1][max(0, min(len(qc) - 3, int(np.searchsorted(qe, v, side="right") - 1)))]
    g["rain_color"] = rain_color
    g["RAIN_COLORS"] = [rain_color(v) for v in g["RAIN_LEVELS"][:-1]]; g["RAIN_OVER"] = "#3d1a0e"   # [MICHAEL 11-3] over 12 in: darker than the umber end (was pale yellow)
    g["THEME"] = T; g["WAVE_SCALES"] = J("qpf_wave_scales.json")
    # waves v4 (Michael, 36 bands: theme/wave_scales_v4.json, exported from design/theme_cd_waves_v4.py) and the snow change scale v6
    g["THEME_WAVES"] = J("wave_scales_v4.json"); g["THEME_SNOWCHG"] = J("michael_design/snow_scale_v6.json")

def encoder_scales(HS):
    """[THEME] scale tables for fast_encode: waves v4 (Hs 0-50 ft, max 0-85 ft) and snow depth change v6.
    Returns {pid: dict(levels, colors, under, over, ticks, cm)}; a None color = no fill (viewer leaves it transparent)."""
    from matplotlib.colors import ListedColormap
    W = HS.THEME_WAVES; out = {}
    def lc(cols, under, over):
        cm = ListedColormap([c or "#00000000" for c in cols]); cm.set_under(under or "#00000000"); cm.set_over(over or "#00000000"); return cm
    for pid, k in (("waves", "wave_height"), ("wavemax", "wave_max")):
        e, c = W[k]["edges_ft"], W[k]["colors"]
        out[pid] = dict(levels=[float(x) for x in e], colors=c[1:-1], under=None, over=c[-1], ticks=W[k]["ticks"], cm=lc(c[1:-1], None, c[-1]))
    S = HS.THEME_SNOWCHG; le, lcol, ge, gcol = S["loss_edges"], S["loss_colors"], S["gain_edges"], S["gain_colors"]
    levels = [float(x) for x in le] + [float(x) for x in ge]          # -24 .. -1, 0.1 .. 60 (the -1..0.1 band = no fill)
    cols = [c.lower() for c in lcol[1:]] + [None] + [c.lower() for c in gcol[:-1]]
    out["dsnod"] = dict(levels=levels, colors=cols, under=lcol[0].lower(), over=gcol[-1].lower(), ticks=[-24, -12, -6, -3, -1, 1, 3, 6, 12, 24, 36, 48, 60],
                        cm=lc(cols, lcol[0], gcol[-1]), outline_over=S["top_outline"])
    return out

def apply_menu_maps(g):
    """g = menu_maps globals(): snow accumulation = Michael snow v6 (amount map)."""
    S = J("michael_design/snow_scale_v6.json"); ge = eval(S["gain_edges"]) if isinstance(S["gain_edges"], str) else S["gain_edges"]
    gc = eval(S["gain_colors"]) if isinstance(S["gain_colors"], str) else S["gain_colors"]
    g["SNOW_LEVELS"] = list(ge); g["SNOW_ANCH"] = list(zip(ge, gc[:-1]))
    g["SNOW_V6"] = S
