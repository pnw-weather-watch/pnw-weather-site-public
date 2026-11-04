"""temp850_scale.py - original 850 mb TEMPERATURE scale (F), v1, Tue Nov 3, 2026 ~7:20 PM PST.
Own anchors (not copied from any site), OKLab-interpolated, bright, on a white base; 2 F bands from -40 to +80 F (60 bands +
under/over). Cold: violet -> indigo -> azure -> sky -> ice (no white; white is the map base). The 32 F line is drawn on top.
Warm: pale lemon -> marigold -> tangerine -> vermilion -> wine. QA: python3 temp850_scale.py -> qa_cvd_temp850_scale.txt"""
import numpy as np, anom_scale as A
import product_scales_light_v1 as _v1
from h500_scale_build_v3 import path_cvd
# lightness rises steadily from the coldest violet to ice at 32 F (so dichromats see order by lightness), then the warm side
# runs pale lemon -> wine. Each side is spaced evenly by the worst-case colour-blind step (path_cvd).
COLD_ANCHORS = ["#2a1448", "#45237e", "#4a3fb4", "#3b6ad6", "#2f93dc", "#4fbad8", "#8fd8d6", "#d3eee6"]   # -40 F -> 32 F
WARM_ANCHORS = ["#f1f3bf", "#f7e07a", "#f8b84c", "#f2843a", "#de4f2f", "#b7283a", "#7f1a3f"]              # 32 F -> 80 F
EDGES = list(range(-40, 81, 2))
COLORS = ["#1c0d33"] + path_cvd(COLD_ANCHORS, 36) + path_cvd(WARM_ANCHORS, 24) + ["#5a0f2e"]   # under, 36 cold, 24 warm, over
T850_TEMP = dict(edges=EDGES, extend="both", unit="°F", colors=COLORS, ticks=[-40, -20, 0, 20, 32, 50, 70, 80], ticks_375=[-40, 0, 32, 80])
_v1.SCALES["t850_temp"] = T850_TEMP
def build(name="t850_temp"): return _v1.build(name)
if __name__ == "__main__":
    import qa_cvd as Q
    c = COLORS; out = [f"temp850_scale v1: {len(c)} colours, 2 F bands -40..80 F. CIE76 dE (Machado 2009), strict neighbour line 5."]
    for k, m in Q.M.items():
        L = Q.sim_lab(c, m); d = np.linalg.norm(np.diff(L, axis=0), axis=1); d2 = np.linalg.norm(L[2:] - L[:-2], axis=1)
        wl = Q.sim_lab(["#ffffff"] + c, m); wmin = min(np.linalg.norm(wl[0] - x) for x in wl[1:])
        out.append(f"{k:7s} neighbour min={d.min():4.1f} mean={d.mean():4.1f} ({'pass' if d.min() >= 5 else 'below 5'})  every-2nd (4 F) min={d2.min():4.1f}  "
                   f"closest colour to white base={wmin:4.1f}")
    open("qa_cvd_temp850_scale.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
