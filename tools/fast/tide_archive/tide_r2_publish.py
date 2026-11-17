#!/usr/bin/env python3
"""Build every station's default tide chart from the incremental CO-OPS store (zero NOAA calls) and upload one JSON per station to R2
bucket pnw-models-data under --prefix (only keys under tide/ are ever written; nothing is deleted). Uses upload_r2.client()
(PNW_R2_ACCESS_KEY_ID / PNW_R2_SECRET_ACCESS_KEY; never printed). The page reads them through /d/<key> like the map data.
  tide_r2_publish.py [--prefix tide/precompute-preview/] [--watch MIN --interval SEC] [--dry-run]
--watch: keep rebuilding every --interval seconds (default 360 = every NOAA 6-min observation) for MIN minutes.

SAFETY: the default prefix is tide/precompute-preview/. Production prefix tide/v1/ (approved by Benjamin, card t390s1748) is
written only when running in GitHub Actions from refs/heads/main (the tide-archive workflow). Do not set WX_R2_PREFIX (that wrapper is for map preview/ keys, not tide/)."""
import os, sys, json, time, argparse, subprocess, tempfile, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
BUCKET = os.environ.get("R2_BUCKET", "pnw-models-data")
import tide_r2_coops as C   # noqa: E402  (prefix rules live in one place)

def check_prefix(prefix, write=True):
    return C.check_prefix(prefix, write)

def download_coops(s3, prefix, dest):
    """Pull the incremental CO-OPS store from R2. The builder must not call NOAA."""
    os.makedirs(dest, exist_ok=True)
    return __import__("tide_r2_coops_ingest", fromlist=["download_store"]).download_store(s3, C.coops_prefix(prefix, write=False), dest)

def publish(prefix, dry, s3):
    out = tempfile.mkdtemp(prefix="tide_r2_")
    coops = tempfile.mkdtemp(prefix="tide_r2_coops_")
    if s3 is not None:
        n = download_coops(s3, prefix, coops)
        if n == 0:
            print("no CO-OPS store in R2; refusing to call NOAA from the builder", flush=True)
            return False
    elif not os.environ.get("TIDE_R2_COOPS"):
        print("no R2 client and TIDE_R2_COOPS unset; refusing to call NOAA from the builder", flush=True)
        return False
    else:
        coops = os.environ["TIDE_R2_COOPS"]
    cmd = [sys.executable, os.path.join(HERE, "tide_r2_build.py"), "--out", out, "--coops", coops]
    if os.environ.get("TIDE_R2_ARCH"): cmd += ["--arch", os.environ["TIDE_R2_ARCH"]]   # fresh local tide-archive checkout
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(r.stdout.strip()); ok = [f for f in sorted(glob.glob(f"{out}/*.json")) if not f.endswith("/index.json")]
    if r.returncode != 0 or not ok: print("build failed; nothing uploaded", r.stderr[-500:] if r.stderr else ""); return False
    n = 0
    for f in ok + [f"{out}/index.json"]:   # stations first, index last
        key = prefix + os.path.basename(f)
        assert key.startswith("tide/") and ".." not in key
        if key.startswith(C.PROD) and not C.v1_write_allowed():
            raise SystemExit("refusing to write a production tide/v1/ key outside the tide-archive workflow on main")
        if not dry: s3.upload_file(f, BUCKET, key, ExtraArgs={"ContentType": "application/json"})
        n += 1
    print(f"{'DRY RUN ' if dry else ''}uploaded {n} files to {prefix} at {time.strftime('%Y-%m-%d %H:%M:%S %Z')}", flush=True)
    return True

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--prefix", default="tide/precompute-preview/"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--watch", type=float, default=0); ap.add_argument("--interval", type=int, default=360); a = ap.parse_args()
    prefix = check_prefix(a.prefix, write=not a.dry_run)
    if os.environ.get("WX_R2_PREFIX"):
        raise SystemExit("WX_R2_PREFIX is set; unset it so tide keys are not rewritten under a map preview/ prefix")
    s3 = None
    if not a.dry_run:
        from upload_r2 import client
        s3 = client()
    end = time.time() + a.watch * 60
    while True:
        t0 = time.time()
        try: publish(prefix, a.dry_run, s3)
        except Exception as e: print("publish error:", type(e).__name__, str(e)[:200], flush=True)
        if time.time() + a.interval > end: break
        time.sleep(max(5, a.interval - (time.time() - t0)))
if __name__ == "__main__": main()
