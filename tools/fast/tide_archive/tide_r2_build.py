#!/usr/bin/env python3
"""Build every station's default tide chart by running tools/fast/site/tide/tide.js headless in Chromium (the same file, the same
browser engine as the page, so the numbers are bit-identical to a live load) and write one JSON per station to --out.
tide_r2_publish.py uploads them to R2. Requires: pip install playwright && python3 -m playwright install chromium.
  tide_r2_build.py [--out DIR] [--site tools/fast/site/tide] [--st 9441102,9447130] [--now MS] [--coops DIR]

Relative requests in tide.js (sst.json, sst_fc.json, ...) are answered from --site. S3 and the GitHub archive are still
fetched live. CO-OPS (datagetter + mdapi) is served only from --coops (the incremental store). The builder makes zero
CO-OPS calls. Pass --allow-live-noaa only for a debug rebuild when the store is missing.
--now builds as of that instant (tests).
PNW Weather: TIDE.build also sets T.state for the WA | CA tab. This script does not write to R2."""
import os, sys, json, time, argparse, asyncio, mimetypes
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ORIGIN = "https://tide-build.invalid"
SHELL = '<!doctype html><meta charset="utf-8"><script>window.TIDE_HEADLESS=true</script><script src="tide.js"></script>'
NOAA = "api.tidesandcurrents.noaa.gov"
ARCH_URL = "https://raw.githubusercontent.com/pnw-weather-watch/pnw-weather-site-public/tide-archive/v1/"   # = tide.js ARCH

async def build(site, out, only, now, coops, allow_live, arch=""):
    os.makedirs(out, exist_ok=True)
    if not coops and not allow_live:
        raise SystemExit("tide_r2_build.py: --coops DIR is required (builder must not call CO-OPS). Use --allow-live-noaa only to debug.")
    if coops:
        import tide_r2_coops as C
    leaked = []
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
        async def noaa(route):
            url = route.request.url
            if NOAA not in url:
                return await route.continue_()
            if not coops:
                leaked.append(url.split("?")[0])
                return await route.continue_()
            got = C.fulfill(coops, url, now or None)
            if not got:
                leaked.append(url)
                return await route.fulfill(status=418, body="coops store does not handle this URL")
            status, ctype, body = got
            if status >= 400:
                # Missing series is a hard builder error, not a live fallback.
                leaked.append(url)
            await route.fulfill(status=status, content_type=ctype, body=body,
                                headers={"access-control-allow-origin": "*"})
        await ctx.route("https://api.tidesandcurrents.noaa.gov/**", noaa)
        if arch:   # --arch: answer tide-archive requests from the checkout the workflow just committed (fresh; no raw CDN lag)
            async def arch_route(route):
                rel = route.request.url[len(ARCH_URL):].split("?")[0]
                f = os.path.join(arch, rel)
                if ".." in rel or not os.path.isfile(f):
                    return await route.fulfill(status=404, body="not found", headers={"access-control-allow-origin": "*"})
                await route.fulfill(status=200, content_type="application/json", body=open(f, "rb").read(), headers={"access-control-allow-origin": "*"})
            await ctx.route(ARCH_URL + "**", arch_route)
        async def new_page():
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            if now: await pg.clock.set_fixed_time(now / 1000.0)
            await pg.goto(ORIGIN + "/tide/?studio=1", wait_until="load"); await pg.wait_for_function("() => window.TIDE && window.TIDE.build")
            return pg
        errs = []
        pg = await new_page()
        keys = only or [s[0] for s in await pg.evaluate("() => TIDE.stations")]
        index = {"schema": 1, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "stations": {}, "coops": bool(coops)}; bad = 0
        for i, key in enumerate(keys):
            t0 = time.time(); last = None
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
        if leaked:
            print("CO-OPS leak or store miss:", leaked[:6], flush=True)
            index["coops_leaks"] = leaked[:20]
            bad = max(bad, 1)
        open(os.path.join(out, "index.json"), "w").write(json.dumps(index)); await br.close()
        return bad, len(keys)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="tide_r2_out"); ap.add_argument("--site", default=os.path.join(HERE, "../site/tide"))
    ap.add_argument("--st", default=""); ap.add_argument("--now", type=int, default=0)
    ap.add_argument("--coops", default=os.environ.get("TIDE_R2_COOPS", ""))
    ap.add_argument("--allow-live-noaa", action="store_true")
    ap.add_argument("--arch", default="", help="local tide-archive v1/ directory to serve instead of raw.githubusercontent.com")
    a = ap.parse_args()
    bad, n = asyncio.run(build(os.path.abspath(a.site), os.path.abspath(a.out), [s for s in a.st.split(",") if s], a.now,
                               os.path.abspath(a.coops) if a.coops else "", a.allow_live_noaa,
                               os.path.abspath(a.arch) if a.arch else ""))
    sys.exit(1 if bad else 0)
if __name__ == "__main__": main()
