"""Point the stripped site's chrome at theme.css (CSS variables) and the canvas chrome at window.WX_THEME. Run once after strip_studio.py."""
import re, sys, pathlib
D = pathlib.Path(sys.argv[1])
CSS = {"#15171c": "var(--bg)", "#262931": "var(--panel)", "#1d2027": "var(--panel2)", "#2c3039": "var(--line)", "#7d828c": "var(--edge)",
       "#8e939c": "var(--edge)", "#f4f2ee": "var(--ink)", "#a7abb3": "var(--muted)", "#2f8cff": "var(--accent)", "#ffd27a": "var(--warn)",
       "#2a2416": "var(--warnbg)", "#6b5a2e": "var(--warnedge)"}
for f in ("index.html", "compare.html", "meteograms.html"):
    p = D / f; s = p.read_text()
    s = re.sub(r'<link rel="preload" href="fonts/Montserrat[^>]*>\n?', "", s)
    s = re.sub(r'@font-face\{font-family:Montserrat[^}]*\}', "", s)
    s = s.replace("Montserrat", "WXTheme")
    for a, b in CSS.items(): s = re.sub(re.escape(a) + r"(?![0-9a-fA-F])", b, s, flags=re.I)
    s = s.replace("</title>", '</title>\n<link rel="stylesheet" href="theme.css">', 1)
    p.write_text(s)
JS = {'"#15171c"': "TH.canvas_bg", '"#f4f2ee"': "TH.canvas_ink", '"#a7abb3"': "TH.canvas_muted", '"#1b1d22"': "TH.dot"}
HEAD = ('// [THEME] canvas chrome colors from theme.css custom properties (edit theme.css, not this file)\n'
        'const TH = (() => { const cs = getComputedStyle(document.documentElement), g = (k, d) => (cs.getPropertyValue(k) || "").trim() || d;\n'
        '  return { canvas_bg: g("--canvas-bg", "#0E1F33"), canvas_ink: g("--canvas-ink", "#F3F7F8"), canvas_muted: g("--canvas-muted", "#9FB3C2"), dot: g("--dot", "#0B2545") }; })();\n')
for f in ("viewer.js", "compare.js", "meteograms.js"):
    p = D / f; s = p.read_text().replace("Montserrat", "WXTheme")
    if f == "viewer.js":
        for a, b in JS.items(): s = s.replace(a, b)
        s = HEAD + s
    p.write_text(s)
print("themed")
