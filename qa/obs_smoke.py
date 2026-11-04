import sys, json
from playwright.sync_api import sync_playwright
base = sys.argv[1]; out = "qa/viewer"
with sync_playwright() as p:
    b = p.chromium.launch(); r = {}
    for dev, a in [("desktop", dict(viewport={"width": 1440, "height": 900})), ("phone", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True))]:
        c = b.new_context(**a); pg = c.new_page(); errs = []
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text)); pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
        pg.goto(base + "index.html", wait_until="networkidle"); pg.wait_for_timeout(2500)
        btn = pg.locator("button", has_text="Observations") if dev == "desktop" else pg.locator("button", has_text="Obs")
        btn.first.click(); pg.wait_for_timeout(9000)
        pg.screenshot(path=f"{out}/observations_{dev}.png"); r[dev] = errs; c.close()
    print(json.dumps(r, indent=1))
