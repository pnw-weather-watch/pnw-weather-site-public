"""Viewer side of the region layer: default view, H/L and ensemble-low tuning for the new views, themed H/L colors.
Values mirror regions/regions.json (hl + default_view). Run after apply_theme_site.py."""
import sys, json, pathlib
D = pathlib.Path(sys.argv[1]); R = json.load(open(sys.argv[2]))
p = D / "viewer.js"; s = p.read_text()
def rep(a, b):
    global s
    if a not in s: sys.exit("MISSING " + a[:60])
    s = s.replace(a, b)
dv = R["default_view"]
rep('view: Q.get("view") || "wa"', f'view: Q.get("view") || "{dv}"')
rep('if (!V[S.view]) S.view = V.wa ? "wa" : Object.keys(V)[0];', f'if (!V[S.view]) S.view = V.{dv} ? "{dv}" : V.pnwhr ? "pnwhr" : Object.keys(V)[0];')
rep('S.view = V.pnw ? "pnw" : "wa";', 'S.view = V.pnw ? "pnw" : Object.keys(V)[0];')
hl = R["hl"]; sm = {"na": 75, "pac": 90, "pnw": 50, "pnwt": 50, "pnwhr": 45, "ca": 45, "hiw": 50}
hlv = {k: [hl["radius_km"].get(k, 400), hl["prominence_mb"].get(k, 2.0), sm.get(k, 50)] for k in sm}
rep('const HL_VIEW = { na: [800, 3.0, 75], pnw: [400, 2.0, 50], pnwt: [400, 2.0, 50], pnwhr: [400, 2.0, 45] };',
    "const HL_VIEW = " + json.dumps(hlv).replace('"', "") .replace("{", "{ ").replace("}", " }") + ";   // [KIT] from regions.json")
rep('const LOWV = { na: [800, 4.0, 1.2], pnw: [400, 1.5, 0.8], pnwt: [300, 1.2, 0.6] };',
    'const LOWV = { na: [800, 4.0, 1.2], pac: [1000, 4.0, 1.4], pnw: [400, 1.5, 0.8], pnwt: [300, 1.2, 0.6], ca: [400, 1.5, 0.6], hiw: [400, 1.5, 0.6] };   // [KIT]')
rep('const HL_LOW_COLOR = "#d7191c", HL_HIGH_COLOR = "#1747c9";',
    'const HL_LOW_COLOR = (getComputedStyle(document.documentElement).getPropertyValue("--map-lo") || "").trim() || "#E4572E", HL_HIGH_COLOR = (getComputedStyle(document.documentElement).getPropertyValue("--map-hi") || "").trim() || "#0B2545";   // [THEME]')
p.write_text(s); print("regions applied")
