"""Smoke test: serve the kit site with any local data/ dir and screenshot desktop + phone; prints console errors."""
import sys, json
from playwright.sync_api import sync_playwright
base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8791/"
out = sys.argv[2] if len(sys.argv) > 2 else "qa/viewer"
pages = [("index.html", "viewer"), ("compare.html", "compare"), ("meteograms.html", "meteograms")]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for dev, ctxargs in [("desktop", dict(viewport={"width": 1440, "height": 900})),
                         ("phone", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True))]:
        for path, name in pages:
            c = b.new_context(**ctxargs); pg = c.new_page(); errs = []; bad = []
            pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
            pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
            pg.on("response", lambda r: r.status >= 400 and bad.append(f"{r.status} {r.url}"))
            pg.goto(base + path, wait_until="networkidle"); pg.wait_for_timeout(4000)
            pg.screenshot(path=f"{out}/{name}_{dev}.png")
            tabs = pg.eval_on_selector_all("#tabs button", "bs => bs.map(b => b.textContent)") if name == "viewer" else []
            res[f"{name}_{dev}"] = dict(console_errors=errs, http_errors=bad, tabs=tabs, drawn=pg.evaluate("window.__drawn || null"))
            c.close()
    b.close()
print(json.dumps(res, indent=1))
