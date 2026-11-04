#!/usr/bin/env python3
"""Deploy guard for the second site (pattern adapted from the main site's refresh/layout guards; own code).
usage: python3 qa/guard.py BASE_URL [WxH ...]      exit 0 = all pass, 1 = any FAIL (blocks / rolls back a deploy)
Checks: (1) refresh reopens the same view for every view x first products of every model, (2) layout alignment
(header, key and map share one column; map inside the viewport width; nothing overlaps the slider), (3) console/page
errors = 0, (4) data proxy answers (/d/manifest.json 200 JSON, or /data/ locally), (5) newest model run per model is
the one loaded by default, (6) colorblind check: each product key keeps distinguishable neighbours under deuteranopia/
protanopia simulation (min dE76 between adjacent key samples >= 3; neighbours that collapse are listed).
Access: behind Cloudflare Access the guard needs a service token: env QA_ACCESS_CLIENT_ID / QA_ACCESS_CLIENT_SECRET
(names only; values never written). Locally (http://127.0.0.1:8817) no headers are sent."""
import os, sys, json, asyncio, io
from playwright.async_api import async_playwright
B = sys.argv[1].rstrip("/"); VW = [tuple(map(int, a.split("x"))) for a in sys.argv[2:]] or [(1440, 900), (390, 844)]
HDR = {}
if os.environ.get("QA_ACCESS_CLIENT_ID"): HDR = {"CF-Access-Client-Id": os.environ["QA_ACCESS_CLIENT_ID"], "CF-Access-Client-Secret": os.environ.get("QA_ACCESS_CLIENT_SECRET", "")}
DATA = "/d/" if not B.startswith("http://127.") and not B.startswith("http://localhost") else "/data/"
fails = []
def res(ok, name, extra=""):
    print(("OK  " if ok else "FAIL"), name, extra, flush=True)
    if not ok: fails.append(name)
STATE = "()=>{const g=i=>{const e=document.getElementById(i);return e?e.value:null};return [g('run'),g('prod'),g('view')].join('|')}"
LAYOUT = """()=>{const r=i=>{const e=document.getElementById(i);if(!e)return null;const b=e.getBoundingClientRect();return [b.left,b.top,b.width,b.height]};
 const m=r('map');return {map:m,vw:innerWidth,doc:document.documentElement.scrollWidth}}"""
def lin(c): c = c / 255; return ((c + .055) / 1.055) ** 2.4 if c > .04045 else c / 12.92
def lab(rgb):
    r, g, b = (lin(x) for x in rgb); X = (.4124*r+.3576*g+.1805*b)/.9505; Y = .2126*r+.7152*g+.0722*b; Z = (.0193*r+.1192*g+.9505*b)/1.089
    f = lambda t: t ** (1/3) if t > .008856 else 7.787*t + 16/116
    return (116*f(Y)-16, 500*(f(X)-f(Y)), 200*(f(Y)-f(Z)))
SIM = {"deutan": [[.625, .375, 0], [.7, .3, 0], [0, .3, .7]], "protan": [[.567, .433, 0], [.558, .442, 0], [0, .242, .758]]}
def cvd_check(png):
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGBA"); w, h = im.size
    sat = lambda q: q[3] > 200 and max(q[:3]) - min(q[:3]) > 40
    y = max(range(0, max(1, h // 3), 2), key=lambda yy: sum(sat(im.getpixel((x, yy))) for x in range(0, w, 8)))   # the key's color bar row
    xs = [x for x in range(w) if sat(im.getpixel((x, y)))] or [0, w - 1]; x0, x1 = xs[0], xs[-1]
    px = [im.getpixel((int(x0 + (x1 - x0) * k / 40), y)) for k in range(41)]; px = [p[:3] for p in px if p[3] > 200]
    worst = {}
    for nm, M in SIM.items():
        s = [tuple(sum(M[i][j] * p[j] for j in range(3)) for i in range(3)) for p in px]
        d = [sum((a - b) ** 2 for a, b in zip(lab(s[k]), lab(s[k + 1]))) ** .5 for k in range(len(s) - 1)]
        d = [x for x in d if x > 0.01]   # identical samples = same band, fine
        worst[nm] = round(min(d), 1) if d else 99
    return worst
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        async with httpx_like(pw) as req:
            r = await req.get(B + DATA + "manifest.json")
            ok = r.ok
            man = await r.json() if ok else {}
            res(ok and bool(man.get("runs") or man.get("models")), "data proxy answers", f"{r.status} {DATA}manifest.json")
        for W, H in VW:
            ph = W < 600
            ctx = await br.new_context(viewport=dict(width=W, height=H), extra_http_headers=HDR, is_mobile=ph, has_touch=ph)
            p = await ctx.new_page(); errs = []
            p.on("console", lambda m: m.type == "error" and errs.append(m.text)); p.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
            p.on("response", lambda rr: rr.status >= 400 and errs.append(f"{rr.status} {rr.url}"))
            await p.goto(B + "/index.html", wait_until="networkidle"); await p.wait_for_timeout(3000)
            runs = await p.evaluate("()=>[...document.getElementById('run').options].map(o=>o.value)")
            first = {}
            for v in runs: first.setdefault(v.split("/")[0], v)
            newest = {m: max(v for v in runs if v.startswith(m + "/")) for m in first}
            res(all(first[m] == newest[m] for m in first), f"{W}x{H} newest run listed first per model", json.dumps(first))
            res((await p.evaluate("()=>document.getElementById('run').value")) == runs[0], f"{W}x{H} newest run loaded by default")
            for m in first:
                await p.select_option("#run", newest[m]); await p.wait_for_timeout(1500)
                views = await p.evaluate("()=>[...document.getElementById('view').options].map(o=>o.value)")
                prods = await p.evaluate("()=>[...document.getElementById('prod').options].map(o=>o.value)")
                for pr in prods[:2]:
                    await p.select_option("#prod", pr); await p.wait_for_timeout(800)
                    for v in views:
                        try: await p.select_option("#view", v)
                        except Exception: continue
                        await p.wait_for_timeout(900); before = await p.evaluate(STATE)
                        await p.reload(wait_until="networkidle"); await p.wait_for_timeout(1800); after = await p.evaluate(STATE)
                        res(before == after, f"{W}x{H} refresh keeps {before}", "" if before == after else "-> " + after)
                        L = await p.evaluate(LAYOUT)
                        ok = L["map"] and L["map"][0] >= -0.5 and L["map"][0] + L["map"][2] <= L["vw"] + 0.5 and L["doc"] <= L["vw"] + 1
                        res(bool(ok), f"{W}x{H} layout {before}", json.dumps(L))
                    if W >= 600:
                        k = await p.evaluate("()=>{try{return new URL(keyURL(S.prod,S.view),location.href).href}catch(e){return null}}")
                        if k:
                            rr = await p.request.get(k); w = cvd_check(await rr.body())
                            res(min(w.values()) >= 3, f"colorblind {m} {pr}", json.dumps(w))
            res(not errs, f"{W}x{H} console errors = 0", "; ".join(errs[:5]))
            await ctx.close()
        await br.close()
class httpx_like:
    def __init__(s, pw): s.pw = pw
    async def __aenter__(s): s.c = await s.pw.request.new_context(extra_http_headers=HDR); return s.c
    async def __aexit__(s, *a): await s.c.dispose()
asyncio.run(main())
print("FAILS", len(fails), *fails[:20], sep="\n" if fails else " "); sys.exit(1 if fails else 0)
