#!/usr/bin/env python3
"""UI console-error sweep on the hidden preview (read-only). Clicks every top tab + toolbar button on desktop and phone,
opens compare/meteograms pages, counts console errors, page errors and HTTP>=400. Access token from env (never printed)."""
import os, sys, json, re
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from _access import scope_sync
B = "https://preview.pnw-weather-site.pages.dev/"
H = {"CF-Access-Client-Id": os.environ["QA_ACCESS_CLIENT_ID"], "CF-Access-Client-Secret": os.environ["QA_ACCESS_CLIENT_SECRET"]}
OUT = "local/shots/20261105"; bad_total = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for dev, a in [("desktop", dict(viewport={"width": 1440, "height": 900})), ("phone", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True))]:
        for page in ["index.html", "compare.html", "meteograms.html"]:
            c = scope_sync(b.new_context(**a)); pg = c.new_page(); errs = []
            pg.on("console", lambda m: m.type == "error" and errs.append("console: " + m.text[:150]))
            pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)[:150]))
            pg.on("response", lambda r: r.status >= 400 and errs.append(f"{r.status} {r.url.split('?')[0]}"))
            pg.goto(B + page, wait_until="networkidle"); pg.wait_for_timeout(3000)
            n = 0
            if page == "index.html":
                SEL = "button"
                labels = pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.textContent.trim())")
                skip = ("Play", "Save image", "Share", "\u2039", "\u203a", "<", ">", "")
                for i, t in enumerate(labels):
                    if t in skip: continue
                    try:
                        ok = pg.evaluate("(i)=>{const b=document.querySelectorAll('button')[i]; if(!b||!b.offsetParent) return false; b.click(); return true}", i)
                        if not ok: continue
                        pg.wait_for_timeout(2500); n += 1
                        if t.split()[0] in ("Observations", "Obs", "Washington", "WA", "California", "CA", "Meteogram", "Waves", "Severe", "Other"):
                            pg.screenshot(path=f"{OUT}/sweep_{re.sub('[^a-z]+','_',t.lower())}_{dev}.png")
                        if pg.url.rstrip("/") != (B + page).rstrip("/") and not pg.url.startswith(B + page): pass
                        pg.goto(B + page, wait_until="networkidle"); pg.wait_for_timeout(1200)
                    except Exception as e: errs.append(f"click {t}: {str(e)[:80]}")
            print(dev, page, "buttons clicked", n, "errors", len(errs), errs[:6]); bad_total += len(errs); c.close()
    b.close()
print("SWEEP_ERRORS", bad_total)
