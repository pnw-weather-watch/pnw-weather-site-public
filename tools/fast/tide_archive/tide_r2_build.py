#!/usr/bin/env python3
"""Build every station's default tide chart by running tools/fast/site/tide/tide.js headless in Chromium (the same file, the same
browser engine as the page, so the numbers are bit-identical to a live load) and write one JSON per station to --out.
tide_r2_publish.py uploads them to R2. Requires: pip install playwright && python3 -m playwright install chromium.
  tide_r2_build.py [--out DIR] [--site tools/fast/site/tide] [--st 9441102,9447130] [--now MS]
Relative requests in tide.js (sst.json, sst_fc.json, ...) are answered from --site (the copies shipped with the site); NOAA,
S3 and the GitHub archive are fetched live exactly as the page does. --now builds as of that instant (tests).
PNW Weather: TIDE.build also sets T.state for the WA | CA tab. This script does not write to R2."""
import os, sys, json, time, argparse, asyncio, mimetypes
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ORIGIN = "https://tide-build.invalid"
SHELL = '<!doctype html><meta charset="utf-8"><script>window.TIDE_HEADLESS=true</script><script src="tide.js"></script>'
async def build(site, out, only, now):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(timezone_id="America/Los_Angeles")
        async def serve(route):
            path = route.request.url[len(ORIGIN + "/tide/"):].split("?")[0] or "index"
            if path == "index": return await route.fulfill(status=200, content_type="text/html", body=SHELL)
            f = os.path.join(site, os.path.basename(path))
            if not os.path.isfile(f): return await route.fulfill(status=404, body="not found")
            await route.fulfill(status=200, content_type=mimetypes.guess_type(f)[0] or "application/octet-stream", body=open(f, "rb").read(),
                                headers={"access-control-allow-origin": "*"})
        await ctx.route(ORIGIN + "/**", serve)
        async def new_page():
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            if now: await pg.clock.set_fixed_time(now / 1000.0)
            await pg.goto(ORIGIN + "/tide/?studio=1", wait_until="load"); await pg.wait_for_function("() => window.TIDE && window.TIDE.build")
            return pg
        errs = []
        pg = await new_page()
        keys = only or [s[0] for s in await pg.evaluate("() => TIDE.stations")]
        index = {"schema": 1, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "stations": {}}; bad = 0
        for i, key in enumerate(keys):
            t0 = time.time(); last = None
            # A long session can hit NOAA "Failed to fetch"; recycle the page and retry up to 3 times.
            if i and i % 10 == 0:
                await pg.close(); pg = await new_page()
            for attempt in range(3):
                try:
                    body = await pg.evaluate("async (k) => JSON.stringify(await TIDE.build(k))", key)
                    snap = json.loads(body); open(os.path.join(out, f"{key}.json"), "w").write(body)
                    index["stations"][key] = {"generated_at": snap["generated_at"], "bytes": len(body), "cond": len(snap["d"]["condOff"]["v"]), "ver": len(snap["d"]["ver"]["v"])}
                    print(f"{key} ok {len(body)} B {int((time.time()-t0)*1000)} ms cond={index['stations'][key]['cond']} ver={index['stations'][key]['ver']}" + (f" retry={attempt}" if attempt else ""), flush=True)
                    last = None; break
                except Exception as e:
                    last = e
                    print(f"{key} attempt {attempt+1} failed {str(e)[:160]}", flush=True)
                    await pg.close(); await asyncio.sleep(2 + attempt); pg = await new_page()
            if last is not None:
                bad += 1; index["stations"][key] = {"error": str(last)[:300]}; print(f"{key} FAILED {str(last)[:200]}", flush=True)
        if errs: print("page errors:", errs[:3])
        open(os.path.join(out, "index.json"), "w").write(json.dumps(index)); await br.close()
        return bad, len(keys)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="tide_r2_out"); ap.add_argument("--site", default=os.path.join(HERE, "../site/tide"))
    ap.add_argument("--st", default=""); ap.add_argument("--now", type=int, default=0); a = ap.parse_args()
    bad, n = asyncio.run(build(os.path.abspath(a.site), os.path.abspath(a.out), [s for s in a.st.split(",") if s], a.now))
    sys.exit(1 if bad == n else 0)
if __name__ == "__main__": main()
