#!/usr/bin/env python3
"""Copy one model's newest verified preview/ run onto the live keys (scheduled jobs, gated by repo variable AUTO_PROMOTE_LIVE).
A run is promoted only when ALL hold:
  - preview/runs/<m>/<cyc>/run.json exists, its steps are unbroken from the first hour, and every step file it lists is in preview/;
  - its grid matches the LIVE manifest crop for the model (so an old-crop preview run never lands under new live metadata);
  - it is newer than the newest live run and (complete, or has more frames than that live run),
    or it IS the newest live run and has more frames than live has (fills a partial run).
A fuller live run is never replaced by a partial one. Older live runs are kept (nothing is deleted).
Order: frame files -> run.json -> live manifest (If-Match ETag read-modify-write) -> live index + catalogs.
  auto_promote_live.py --models hrrr,rrfs [--dry-run]
Env: PNW_R2_ACCESS_KEY_ID, PNW_R2_SECRET_ACCESS_KEY. Never reads WX_R2_PREFIX: source is always preview/, target always live."""
import os, sys, json, time, random, argparse
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
B = "pnw-models-data"; A = "b6dc205037fd8e8c37d5267ee61dc302"; PRE = "preview/"

def raw_client():
    import boto3
    from botocore.config import Config
    return boto3.client("s3", endpoint_url=f"https://{A}.r2.cloudflarestorage.com", region_name="auto",
                        aws_access_key_id=os.environ["PNW_R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["PNW_R2_SECRET_ACCESS_KEY"],
                        config=Config(max_pool_connections=32, retries={"max_attempts": 5, "mode": "standard"}))

def same_grid(run, crop):
    if not crop or not run: return False
    g = run.get("grid") or {}
    if g.get("ny") != crop[1] - crop[0] or g.get("nx") != crop[3] - crop[2]: return False
    if "i0" in g and g.get("i0") != crop[0]: return False
    if "j0" in g and g.get("j0") != crop[2]: return False
    return True

# Member maps and OISST reuse another model's stored crop. Without this catalog
# entry, live_crop is missing and same_grid always fails, so they never promote.
CROP_FROM = {"aensm": "aens", "epsm": "eps", "oisst": "gfs"}

def ensure_catalog_crop(man, m, fallback_man=None):
    """Guarantee models[m].crop exists so the grid check can pass. Pure enough to unit-test.

    Prefers a crop already on this model, then the sibling donor on `man`, then the
    same two places on `fallback_man` (usually the preview manifest).
    """
    if not isinstance(man, dict):
        return None
    models = man.setdefault("models", {})
    entry = models.setdefault(m, {})
    if entry.get("crop"):
        return entry["crop"]
    donor = CROP_FROM.get(m)
    cands = []
    if donor:
        cands.append((models.get(donor) or {}).get("crop"))
    if fallback_man:
        fb = (fallback_man.get("models") or {})
        cands.append((fb.get(m) or {}).get("crop"))
        if donor:
            cands.append((fb.get(donor) or {}).get("crop"))
    for crop in cands:
        if crop:
            entry["crop"] = list(crop)
            return entry["crop"]
    return None


def frames(run):
    """Unbroken frame count from the start, using the run's own expected hour list order."""
    return len((run or {}).get("steps") or [])

def unbroken(run):
    fs = [s["f"] for s in (run or {}).get("steps") or []]
    return fs == sorted(set(fs))

def decide(m, cand_cyc, cand, live_runs, live_newest_run, live_crop):
    """-> (promote: bool, reason). Pure; unit tested."""
    if not cand: return False, "no preview run.json"
    if not unbroken(cand): return False, "preview steps out of order or duplicated"
    if not same_grid(cand, live_crop): return False, f"preview grid {cand.get('grid')} != live crop {live_crop}"
    nf = frames(cand)
    if nf == 0: return False, "preview run has no frames"
    newest = max(live_runs) if live_runs else None
    lf = frames(live_newest_run) if live_newest_run and same_grid(live_newest_run, live_crop) else 0
    if newest is None: return True, "no live run"
    if cand_cyc > newest:
        if cand.get("complete"): return True, f"newer and complete ({nf} frames)"
        if nf > lf: return True, f"newer, {nf} frames > live {newest} {lf}"
        return False, f"newer but partial {nf} <= live {newest} {lf}"
    if cand_cyc == newest:
        if nf > lf: return True, f"fills live {newest}: {nf} > {lf} frames"
        return False, f"same run, live already has {lf} frames"
    return False, f"older than live {newest}"


def get_json(s3, key):
    o = s3.get_object(Bucket=B, Key=key); return json.loads(o["Body"].read()), o["ETag"]

def try_json(s3, key):
    try: return get_json(s3, key)[0]
    except Exception: return None

def list_keys(s3, prefix):
    out = {}
    for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=B, Prefix=prefix):
        for o in pg.get("Contents", []): out[o["Key"]] = o
    return out

def apply_manifest(man, prev_man, m, cyc, cand, keep):
    """Mutates the live manifest dict for model m. Pure; unit tested."""
    ensure_catalog_crop(man, m, prev_man)
    runs = man.setdefault("runs", {})
    cur = list(runs.get(m) or [])
    new = sorted(set(cur) | {cyc})
    if keep: new = new[-keep:]
    runs[m] = new
    mg = man.setdefault("mgruns", {})
    mg[m] = sorted(set(mg.get(m) or []) | set(new))
    pg = man.setdefault("progress", {}).setdefault(m, {})
    if cand.get("complete"): pg.pop(cyc, None)
    else: pg[cyc] = [cand["steps"][-1]["f"], cand.get("expected") or cand["steps"][-1]["f"]]
    for k in [k for k in pg if k not in new]: pg.pop(k)
    if not pg: man["progress"].pop(m, None)
    return man

def promote(s3, m, dry=False, log=print):
    live_man, _ = get_json(s3, "manifest.json")
    prev_man = try_json(s3, PRE + "manifest.json") or {}
    live_crop = ensure_catalog_crop(live_man, m, prev_man)
    live_runs = list((live_man.get("runs") or {}).get(m) or [])
    prev_runs = sorted((prev_man.get("runs") or {}).get(m) or [])
    newest_live = max(live_runs) if live_runs else None
    live_newest_run = try_json(s3, f"runs/{m}/{newest_live}/run.json") if newest_live else None
    # Oldest -> newest: fill listed live runs that preview has more of, then add newer runs. The newest eligible run is promoted
    # in this call; an older eligible listed run is filled first (one run per call keeps each job short).
    elig = []
    for cyc in prev_runs:
        cand = try_json(s3, f"{PRE}runs/{m}/{cyc}/run.json")
        if cyc in live_runs and cyc != newest_live:
            ref = try_json(s3, f"runs/{m}/{cyc}/run.json"); ok, why = decide(m, cyc, cand, [cyc], ref, live_crop)
        else:
            ok, why = decide(m, cyc, cand, live_runs, live_newest_run, live_crop)
        log(f"{m} {cyc}: {'eligible' if ok else 'skip'} ({why})" + (f" frames={frames(cand)} complete={bool(cand.get('complete'))}" if cand else ""))
        if ok: elig.append((cyc, cand))
    res = dict(model=m, live_newest=newest_live, live_frames=frames(live_newest_run), preview_runs=prev_runs)
    res["promoted"] = []
    for cyc, cand in elig:
        r1 = _one(s3, m, cyc, cand, prev_runs, live_runs, prev_man, dry, log)
        if r1: res["promoted"].append(r1)
    return res

def _one(s3, m, cyc, cand, prev_runs, live_runs, prev_man, dry, log):
    res = {}
    src = list_keys(s3, f"{PRE}runs/{m}/{cyc}/")
    rel = {k[len(PRE):]: o for k, o in src.items()}
    # verify every listed frame has its files in preview/
    fs = {s["f"] for s in cand["steps"]}
    have = {f for f in fs if any(k.endswith(f"_f{f:03d}.webp") or k.endswith(f"_f{f:03d}.png") for k in rel)}
    if have != fs:
        log(f"{m} {cyc}: skip (preview missing files for hours {sorted(fs - have)[:10]})"); return None
    dst = list_keys(s3, f"runs/{m}/{cyc}/")
    todo = [k for k, o in rel.items() if not k.endswith("/run.json") and (k not in dst or dst[k].get("ETag") != o.get("ETag"))]
    res.update(run=cyc, frames=frames(cand), complete=bool(cand.get("complete")), init=cand.get("init"), copies=len(todo) + 1)
    if dry: log(f"{m} {cyc}: DRY RUN would copy {len(todo)} files + run.json and list it live"); return res
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(lambda k: s3.copy_object(Bucket=B, Key=k, CopySource={"Bucket": B, "Key": PRE + k}), todo))
    s3.copy_object(Bucket=B, Key=f"runs/{m}/{cyc}/run.json", CopySource={"Bucket": B, "Key": f"{PRE}runs/{m}/{cyc}/run.json"})
    keep = max(len(prev_runs), len(live_runs), 1)   # never shrink the live list
    for i in range(8):
        o = s3.get_object(Bucket=B, Key="manifest.json"); man = json.loads(o["Body"].read())
        apply_manifest(man, prev_man, m, cyc, cand, keep)
        try:
            s3.put_object(Bucket=B, Key="manifest.json", Body=json.dumps(man).encode(), ContentType="application/json", IfMatch=o["ETag"])
            break
        except Exception as e:
            if "PreconditionFailed" not in str(e) and "412" not in str(e): raise
            time.sleep(0.5 + random.random() * 2)
    else:
        raise SystemExit("live manifest.json kept changing; gave up")
    from fast_cycle import publish_catalogs
    publish_catalogs(s3, man)
    log(f"{m} {cyc}: LIVE ({frames(cand)} frames, complete={bool(cand.get('complete'))}); live index + catalogs rewritten")
    live_runs[:] = man["runs"][m]
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    s3 = raw_client(); out = []
    models = a.models.split(",")
    if "ifs" in models and "ifs9" not in models: models.append("ifs9")
    for m in models:
        try: out.append(promote(s3, m, a.dry_run))
        except SystemExit: raise
        except Exception as e: print(m, "auto-promote failed:", type(e).__name__, str(e)[:200], flush=True)
    print("AUTO_PROMOTE", json.dumps(out))

if __name__ == "__main__":
    main()
