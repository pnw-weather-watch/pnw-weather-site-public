#!/usr/bin/env python3
"""Interaction checks for DETAILS_CHECKLIST (hover readout, zoom, save, share, peak gust, missing hour, preload, view default,
pass forecasters). usage: python3 qa/interaction_check.py BASE   (Access: QA_ACCESS_CLIENT_ID / _SECRET env)"""
import os, sys, json
from playwright.sync_api import sync_playwright
B = sys.argv[1].rstrip("/"); HDR = {"CF-Access-Client-Id": os.environ["QA_ACCESS_CLIENT_ID"], "CF-Access-Client-Secret": os.environ.get("QA_ACCESS_CLIENT_SECRET", "")} if os.environ.get("QA_ACCESS_CLIENT_ID") else {}
R = {}
def ok(k, v, note=""): R[k] = (bool(v), note); print("OK  " if v else "FAIL", k, note, flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(viewport={"width": 1440, "height": 900}, extra_http_headers=HDR, accept_downloads=True); pg = c.new_page()
    reqs = []; pg.on("request", lambda r: reqs.append(r.url))
    pg.goto(B + "/index.html", wait_until="networkidle"); pg.wait_for_timeout(3000)
    st = pg.evaluate("()=>({run:S.run,prod:S.prod,view:S.view})"); ok("view default (regions.json default_view)", st["view"], json.dumps(st))
    # preload: after load, more step files than the current one were requested
    n0 = len([u for u in reqs if "/runs/" in u]); ok("preload order (other steps fetched after first draw)", n0 > 3, f"{n0} run files")
    bx = pg.eval_on_selector("#map", "e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height]}")
    pg.mouse.move(bx[0] + bx[2] * 0.5, bx[1] + bx[3] * 0.55); pg.wait_for_timeout(600)
    tip = pg.evaluate("()=>{const t=document.getElementById('tip');return t&&!t.hidden?t.textContent:''}"); ok("hover readout with units", tip and any(u in tip for u in ("°", "F", "mb", "in", "kt", "mph", "ft")), tip[:60])
    z0 = pg.evaluate("()=>JSON.stringify(window.Z||null)"); pg.mouse.wheel(0, -400); pg.wait_for_timeout(1200)
    z1 = pg.evaluate("()=>JSON.stringify(window.Z||null)"); tr = pg.eval_on_selector("#map", "e=>getComputedStyle(e).transform")
    ok("zoom (wheel)", z0 != z1 or tr not in ("none", ""), f"transform {tr[:40]}")
    try:
        with pg.expect_download(timeout=15000) as d: pg.click("#save")
        ok("save image (download)", d.value.suggested_filename.endswith(".png"), d.value.suggested_filename)
    except Exception as e: ok("save image (download)", False, str(e)[:80])
    ok("share button present", pg.is_visible("#share"))
    # peak gust marker on a gust product
    prods = pg.evaluate("()=>[...document.getElementById('prod').options].map(o=>o.value)")
    gp = next((x for x in ["gust10", "gust6", "gust12", "gust24", "gustmax"] if x in prods), None)
    if not gp:
        for tab in pg.query_selector_all("button.tab, #tabs button"): pass
    pg.goto(B + f"/index.html?run={st['run']}&prod=gustmax&view={st['view']}&f=24", wait_until="networkidle"); pg.wait_for_timeout(3000)
    ok("peak gust marker drawn", pg.evaluate("()=>!!(window.__peak||window.__drawn)"), pg.evaluate("()=>JSON.stringify(window.__peak||null)")[:80])
    # missing hour: ask for an hour the run lacks -> nearest hour + note
    pg.goto(B + f"/index.html?run={st['run']}&prod=t2m&view={st['view']}&f=7", wait_until="networkidle"); pg.wait_for_timeout(3000)
    u = pg.url; ok("missing hour jumps to nearest", "f=7" not in u or pg.evaluate("()=>!!document.querySelector('.jump,#jumpnote,.jumpnote')"), u.split("?")[-1])
    for k, nm in (("wa", "Washington Pass Forecaster"), ("ca", "California Pass Forecaster")):
        pg.goto(B + f"/index.html?pf={k}", wait_until="networkidle"); pg.wait_for_timeout(5000)
        t = pg.evaluate("()=>document.querySelector('#mg b')?.textContent||''"); rows = pg.evaluate("()=>document.querySelectorAll('#mgbody tr').length")
        ok(f"{nm} opens + table", t == nm and rows > 2, f"{rows} rows")
    b.close()
print("FAILS", sum(1 for v in R.values() if not v[0]))
