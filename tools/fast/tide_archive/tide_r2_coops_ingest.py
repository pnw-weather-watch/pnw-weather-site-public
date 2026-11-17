#!/usr/bin/env python3
"""Paced incremental CO-OPS ingest for the preview precompute store.

Appends only new hours of predictions, water_level and air_pressure (and
refreshes mdapi at most daily) under tide/precompute-preview/coops/. Keeps the
30-day series the Tides page needs. Refuses to start during a tide-archive
slot unless --force. Does not write tide/v1/.

  tide_r2_coops_ingest.py [--out DIR] [--prefix tide/precompute-preview/] [--upload]
                          [--st 9441102,9447130] [--force] [--full] [--no-preds]
                          [--download]   # pull existing store from R2 first

This script is what talks to CO-OPS. The Actions chart builder must not call it;
it only reads the store from R2. Run this on a box that is not the archive
Actions egress, or from a hook that imports an archive --dump-coops (zero extra
calls) and then only fills gaps the snapshot did not cover (30-day pressure).
"""
import argparse, json, os, sys, time, datetime as D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import tide_r2_coops as C

PRODUCTS = ("predictions", "water_level", "air_pressure")


def r2_client():
    if os.environ.get("WX_R2_PREFIX"):
        raise SystemExit("WX_R2_PREFIX is set; unset it so tide keys are not rewritten")
    from upload_r2 import client
    return client()


def download_store(s3, prefix, out):
    token = None
    n = 0
    while True:
        kw = dict(Bucket=C.BUCKET, Prefix=prefix)
        if token:
            kw["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kw)
        for obj in resp.get("Contents") or []:
            key = obj["Key"]
            if not key.startswith(prefix) or key.startswith("tide/v1/"):
                raise SystemExit(f"refuse unexpected key {key}")
            rel = key[len(prefix):]
            if not rel or rel.endswith("/"):
                continue
            dest = os.path.join(out, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            s3.download_file(C.BUCKET, key, dest)
            n += 1
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
    print(f"downloaded {n} objects from {prefix}", flush=True)
    return n


def upload_store(s3, prefix, out, only=None):
    n = 0
    for root, _, files in os.walk(out):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, out)
            if only is not None and path not in only and os.path.basename(path) != "index.json":
                # still upload index
                if fn != "index.json":
                    continue
            key = prefix + rel.replace("\\", "/")
            if key.startswith("tide/v1/") or not key.startswith(prefix):
                raise SystemExit(f"refuse key {key}")
            s3.upload_file(path, C.BUCKET, key, ExtraArgs={"ContentType": "application/json"})
            n += 1
    print(f"uploaded {n} objects to {prefix}", flush=True)
    return n


def import_dump(dump_dir, out, now):
    """Merge a tide_archive.py --dump-coops tree (zero CO-OPS). Returns counts."""
    n = 0
    if not dump_dir or not os.path.isdir(dump_dir):
        return 0
    for st in os.listdir(dump_dir):
        d = os.path.join(dump_dir, st)
        if not os.path.isdir(d):
            continue
        for product in PRODUCTS:
            src = os.path.join(d, f"{product}.json")
            if not os.path.isfile(src):
                continue
            incoming = json.load(open(src))
            pts = incoming.get("pts") or []
            rec = C.load_series(out, st, product)
            rec["pts"] = C.merge_pts(rec.get("pts") or [], pts, now - C.KEEP_PAST)
            rec["station"], rec["product"] = st, product
            rec["updated"] = incoming.get("updated") or D.datetime.now(D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            rec["last_t"] = rec["pts"][-1][0] if rec["pts"] else None
            rec["first_t"] = rec["pts"][0][0] if rec["pts"] else None
            rec["n"] = len(rec["pts"])
            rec["source"] = "archive-dump"
            C.save_series(out, rec)
            n += 1
    print(f"imported {n} series from dump {dump_dir}", flush=True)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/tide_r2_coops")
    ap.add_argument("--prefix", default="tide/precompute-preview/")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--download", action="store_true", help="refresh --out from R2 before ingesting")
    ap.add_argument("--st", default="")
    ap.add_argument("--force", action="store_true", help="run even inside a tide-archive blackout")
    ap.add_argument("--full", action="store_true", help="re-pull the full 30-day window (seed / repair)")
    ap.add_argument("--no-preds", action="store_true", help="skip predictions (use when they already cover the lead)")
    ap.add_argument("--dump", default="", help="merge a --dump-coops directory first (no CO-OPS)")
    ap.add_argument("--pace", type=float, default=0.35)
    a = ap.parse_args()
    prefix = C.coops_prefix(a.prefix)
    blocked, why = C.archive_blackout()
    if blocked and not a.force:
        print(f"SKIP {why}"); return 0
    os.makedirs(a.out, exist_ok=True)
    C.set_pace(a.pace)
    s3 = None
    if a.upload or a.download:
        s3 = r2_client()
    if a.download:
        download_store(s3, prefix, a.out)
    now = C.now_ms()
    if a.dump:
        import_dump(a.dump, a.out, now)
    sts = [s for s in a.st.split(",") if s] or list(C.STATIONS)
    # Always ingest neighbor gauges for pressure, even if --st is a subset.
    if a.st:
        extra = []
        for st in list(sts):
            extra.extend(C.P_NEIGHBORS.get(st, []))
        sts = list(dict.fromkeys(sts + extra))
    t0 = time.time()
    total_calls = 0
    rows = []
    products = [("water_level", False), ("air_pressure", False)]
    if not a.no_preds:
        products.insert(0, ("predictions", False))
    for st in sts:
        recs = {}
        for product, _ in products:
            rec = C.update_product(a.out, st, product, now, force_full=a.full)
            total_calls += rec.get("calls") or 0
            recs[product] = rec
        meta_calls = C.update_meta(a.out, st, now)
        total_calls += meta_calls
        rows.append({
            "st": st,
            "calls": sum((recs[p].get("calls") or 0) for p, _ in products) + meta_calls,
            "pred_n": (recs.get("predictions") or {}).get("n"),
            "wl_n": recs["water_level"].get("n"),
            "air_n": recs["air_pressure"].get("n"),
            "fetched": {p: recs[p].get("fetched") for p, _ in products},
        })
        print(
            f"{st} calls={rows[-1]['calls']} pred={rows[-1]['pred_n']} wl={rows[-1]['wl_n']} air={rows[-1]['air_n']}"
            + (f" windows={rows[-1]['fetched']}" if any(recs[p].get("calls") for p, _ in products) else " (store current)"),
            flush=True,
        )
    stats = {
        "updated": D.datetime.now(D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stations": sts,
        "calls": total_calls,
        "elapsed_s": round(time.time() - t0, 1),
        "full": a.full,
        "prefix": prefix,
        "rows": rows,
    }
    C.write_index(a.out, {k: stats[k] for k in ("updated", "stations", "calls", "elapsed_s", "full", "prefix")})
    print(json.dumps({k: stats[k] for k in ("updated", "calls", "elapsed_s", "full", "prefix")}), flush=True)
    if a.upload:
        upload_store(s3, prefix, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
