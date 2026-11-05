"""Full-size screenshots of the hidden preview (Access service token from env, never printed). usage: preview_shots.py name=query ..."""
import sys, os
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'qa')); from _access import scope_sync
B = "https://preview.pnw-weather-site.pages.dev/index.html"
H = {"CF-Access-Client-Id": os.environ["QA_ACCESS_CLIENT_ID"], "CF-Access-Client-Secret": os.environ["QA_ACCESS_CLIENT_SECRET"]}
with sync_playwright() as p:
    b = p.chromium.launch()
    for dev, a in [("desktop", dict(viewport={"width": 1440, "height": 900})), ("phone", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True))]:
        for arg in sys.argv[1:]:
            name, q = arg.split("=", 1)
            c = scope_sync(b.new_context(**a)); pg = c.new_page(); errs = []
            pg.on("response", lambda r: r.status >= 400 and errs.append(f"{r.status} {r.url.split('?')[0]}"))
            pg.goto(B + "?" + q, wait_until="networkidle"); pg.wait_for_timeout(4000)
            pg.screenshot(path=f"local/shots/20261104/{name}_{dev}.png", full_page=True); print(name, dev, errs[:3]); c.close()
    b.close()
