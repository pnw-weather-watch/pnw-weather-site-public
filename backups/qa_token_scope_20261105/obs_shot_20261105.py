import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'qa')); from _access import scope_sync
from playwright.sync_api import sync_playwright
B = "https://preview.pnw-weather-site.pages.dev/index.html"
with sync_playwright() as p:
    b = p.chromium.launch()
    for dev, a, name in [("desktop", dict(viewport={"width": 1440, "height": 900}), "Observations"), ("phone", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True), "Obs")]:
        c = scope_sync(b.new_context(**a)); pg = c.new_page(); errs = []
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text[:140])); pg.on("pageerror", lambda e: errs.append(str(e)[:140]))
        pg.goto(B, wait_until="networkidle"); pg.wait_for_timeout(2000)
        pg.get_by_role("button", name=name, exact=True).click(); pg.wait_for_timeout(8000)
        pg.screenshot(path=f"local/shots/20261105/sweep_obs_{dev}.png"); print(dev, pg.url[-40:], errs); c.close()
    b.close()
