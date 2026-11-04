"""Strip Studio / Social / WA Maps / reqbox code from a copy of the viewer. Run on the KIT copy only."""
import re, sys, pathlib
D = pathlib.Path(sys.argv[1])
def sub(path, pairs):
    p = D / path; s = p.read_text()
    for a, b in pairs:
        n = s.count(a) if isinstance(a, str) else len(re.findall(a, s))
        if n == 0: sys.exit(f"MISSING in {path}: {a[:70]!r}")
        s = s.replace(a, b) if isinstance(a, str) else re.sub(a, b, s)
    p.write_text(s)
L = lambda s: re.compile(r"^.*" + re.escape(s) + r".*\n", re.M)   # drop whole line
sub("viewer.js", [
 (L('if (Q.get("studio")) return Math.max(1'), ""),
 (re.compile(r"^// 10-31 6:44 PM \(Benjamin: \"Scrubbing.*?finger lifts\.\n", re.M | re.S), ""),
 (L("const STUDIO_DRAG_RS = 1;"), ""),
 ('keepRS && Q.get("studio") && S.dragging ? STUDIO_DRAG_RS : ', ""),
 (re.compile(r"^// 10-31 7:30 PM \(Benjamin: \"a slightly more zoomed-out.*?^}\n", re.M | re.S), ""),
 (L('Q.get("studio") ? fetch(DATA + "static/studio_views.json"'), ""),
 ("const [man, sv, vf, wv] =", "const [man, vf, wv] ="),
 (L("if (PV && PV.studio && sv)"), ""),
 ("S.man = addStudioViews(waveViews(viewFixes(mergeRunsX(man), vf), wv), sv);", "S.man = waveViews(viewFixes(mergeRunsX(man), vf), wv);"),
 (L("// WA Maps (10-31, Benjamin 8:58 AM)"), ""),
 ('(Q.get("embed") || Q.get("studio") ? "" : `<button type="button" data-t="wamaps" title="Washington state-view forecast maps">WA Maps</button>` +\n', '(Q.get("embed") ? "" :\n'),
 ('Compare</button>` +\n', 'Compare</button>`);\n'),
 (L('data-t="studio" title="Studio'), ""), (L('data-t="social" title="Social'), ""),
 ('if (b && b.dataset.t === "wamaps") { location.href = "wamaps.html"; return; }\n', "\n"),
 (L('b.dataset.t === "social"'), ""), (L('b.dataset.t === "studio"'), ""),
 ("   // Studio-only view: Washington key", ""),
 ('const lite = !!S.dragging && !(FINE_PTR && Q.get("studio"));', "const lite = !!S.dragging;"),
 ("; if (window.onStudioSkip) window.onStudioSkip();", ";"),
 (' && !Q.get("studio")) paintLowPanel', ") paintLowPanel"),
 ('if (!V.studioOnly) ctx.drawImage(L2.key, 0, 0, LW, LH);   // Studio-only view: Studio draws its own color bar (the key file is another view\'s)', "ctx.drawImage(L2.key, 0, 0, LW, LH);"),
 ("if (!V.studioOnly) drawCredit(", "drawCredit("),
 ('if (lite) { if (window.onStudioDraw && Q.get("studio")) window.onStudioDraw(cv_(), S.cur, step, true); return; }', "if (lite) return;"),
 (L("if (window.onStudioDraw) window.onStudioDraw(cv_(), S.cur, step);"), ""),
 (re.compile(r"^.*window\.studioLabelHidden && Q\.get\(\"studio\"\).*\n.*\n", re.M), ""),
 (L("// 11-03: Studio hides line labels"), ""),
])
sub("index.html", [(L('reqbox.js'), ""), (" MP4 export: mp4-muxer (MIT).", "")])
sub("compare.html", [(L('#hbar #tv{'), ""), (re.compile(r'\n  <button type="button" id="tv".*?TV 16:9</button>'), ""), (" MP4 export: mp4-muxer (MIT).", ""),
  ('Main map (widescreen, for TV / YouTube)', 'Main map')])
sub("compare.js", [(re.compile(r'^\$\("tv"\)\.onclick = .*?\n.*?\n.*?\n', re.M), "")])
print("stripped ok")
# final pass: comments that still mention Studio (code on those lines is shared viewer code and stays)
for f in ("viewer.js", "compare.js", "meteograms.js"):
    p = D / f; out = []
    for line in p.read_text().split("\n"):
        if re.search(r"studio", line, re.I):
            st = line.lstrip()
            if st.startswith("//"): continue
            i = line.find("   // ")
            if i > 0: line = line[:i]
        out.append(line)
    p.write_text("\n".join(out))
    left = [l for l in out if re.search(r"studio|social|wamaps|reqbox", l, re.I)]
    if left: sys.exit(f"{f} still has: {left[:3]}")
print("comments clean")
# preview supplement (pdata/manifest_pv.json) only with ?pv=1 (no 404 on normal loads)
sub("viewer.js", [('PV = await fetch("pdata/manifest_pv.json"', 'PV = !Q.get("pv") ? null : await fetch("pdata/manifest_pv.json"')])
