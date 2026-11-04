"""FROZEN copy of the v6 snow scale (superseded by snow_scale.py v7; kept so v6 mocks reproduce). Originally: THE site-wide snow scale (v6, Tue Nov 3, 2026, PST). Use it for every snow map on this site: snow depth change,
snow depth, snowfall totals, pass cards and meteogram chips. Benjamin (v5 feedback): "Add about double of the amount of
transitional colors, and increase the top end to 60 in. ... that will be the scale for all snow maps on this site."

Hue path (same as v4/v5, twice the steps): gain = light blue -> blues -> deep indigo -> violet -> purple -> magenta -> pink,
white for 60 in and up; loss (change maps only) = deep red -> rust -> orange -> pale amber; -1 to +0.1 in = no fill.
Colors are CIELAB-interpolated between hand-picked anchors (lightness falls through the blues to the indigo at 12-15 in,
then rises steadily to white) and pass qa_cvd.py (Machado 2009 deutan/protan/tritan, neighbour dE >= 6.7).
The white top bin always gets a dark outline (TOP_OUTLINE) on keys and chips, plus a thin dark contour at 60 in on maps.
snow_scale.json holds the same edges and colors for the site front end; regenerate it with `python3 snow_scale.py`.
"""
import json, os
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm, to_rgba

UNIT = "in"
TOP_OUTLINE = "#06101A"
NOFILL = (-1.0, 0.1)                      # little or no change: transparent
LOSS_EDGES = [-24, -18, -12, -9, -6, -4.5, -3, -2, -1]
GAIN_EDGES = [0.1, 0.5, 1, 2, 3, 4.5, 6, 9, 12, 15, 18, 21, 24, 30, 36, 42, 48, 54, 60]
# loss: under (< -24) then the 8 loss bins, deepest first
LOSS_COLORS = ["#5E1A20", "#762425", "#8E2F2A", "#A63F2C", "#BF4F2D", "#CE6832", "#DC8038", "#EAA865", "#F3CF92"]
# gain: the 18 bins 0.1-0.5 ... 54-60, then the over color (60+)
GAIN_COLORS = ["#CDE8F9", "#B1D7F3", "#93C6EC", "#79B1E3", "#5C9CD9", "#4C84CD", "#3A6CC0", "#2E4AA6", "#22247C", "#3E2A9C", "#6036B4", "#8444C2", "#A652D0", "#BD60CE", "#D26ECC", "#E084D1", "#EE9AD6", "#F8C6E6", "#FFFFFF"]

def _fmt(v): return f"{v:g}"

def labels(kind="change"):
    g = [f"{_fmt(a)}-{_fmt(b)}" for a, b in zip(GAIN_EDGES[:-1], GAIN_EDGES[1:])] + [f"{_fmt(GAIN_EDGES[-1])}+"]
    if kind != "change": return g
    l = [f"< {_fmt(LOSS_EDGES[0])}"] + [f"{_fmt(a)} to {_fmt(b)}" for a, b in zip(LOSS_EDGES[:-1], LOSS_EDGES[1:])]
    return l + ["-1 to 0.1 (no fill)"] + g

def build(kind="change"):
    """(cmap, norm, edges). kind="change": diverging, melt bins + transparent -1..0.1 + gain bins, extend both.
    kind="amount" (snow depth, snowfall totals): gain bins only, < 0.1 in transparent, extend max."""
    if kind == "change":
        edges = np.asarray(LOSS_EDGES + GAIN_EDGES, float)
        inner = [to_rgba(c) for c in LOSS_COLORS[1:]] + [(0, 0, 0, 0)] + [to_rgba(c) for c in GAIN_COLORS[:-1]]
        cmap = ListedColormap(inner); cmap.set_under(to_rgba(LOSS_COLORS[0]))
    elif kind == "amount":
        edges = np.asarray(GAIN_EDGES, float)
        cmap = ListedColormap([to_rgba(c) for c in GAIN_COLORS[:-1]]); cmap.set_under((0, 0, 0, 0))
    else:
        raise ValueError(kind)
    cmap.set_over(to_rgba(GAIN_COLORS[-1]))
    return cmap, BoundaryNorm(edges, cmap.N), edges

def as_dict():
    return dict(name="site snow scale", version="v6", unit=UNIT, top_outline=TOP_OUTLINE, nofill=list(NOFILL),
                loss_edges=LOSS_EDGES, gain_edges=GAIN_EDGES, loss_colors=LOSS_COLORS, gain_colors=GAIN_COLORS,
                change_labels=labels("change"), amount_labels=labels("amount"),
                notes="change maps: loss_colors[0] = under (< -24), loss_colors[1:] = loss bins, -1..0.1 transparent, "
                      "gain_colors[:-1] = gain bins, gain_colors[-1] = over (60+, white, dark outline). "
                      "amount maps: < 0.1 transparent, gain bins, 60+ white.")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snow_scale_v6.json")
    json.dump(as_dict(), open(out, "w"), indent=1); print(out)
