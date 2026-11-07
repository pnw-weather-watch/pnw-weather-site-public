#!/usr/bin/env python3
"""One pass of the fast-style publisher (GitHub Actions, every 15 min; also runnable on the box).
For each model: newest cycle whose first step is out -> encode the steps that are out and not yet in R2 -> upload them,
then run.json (only the unbroken steps from the start, so the slider has no holes) -> manifest lists the newest `keep` runs
whose run.json is in R2 -> prune older runs. Never touches the Pages projects. WX_R2_PREFIX=preview/ writes the shared preview. WX_R2_PREFIX=preview-pr16/ writes that deployment's prefix and leaves preview/ and the live keys alone.
  fast_cycle.py [--models hrrr,gfs,ifs,aifs] [--minutes 40] [--workers 4] [--dry-run]
Env: PNW_R2_ACCESS_KEY_ID, PNW_R2_SECRET_ACCESS_KEY. Optional WX_R2_PREFIX (preview/ by default in the workflow; preview-pr16/ for that Pages alias)."""
import os, sys, json, time, argparse, datetime as dt, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fast_encode as FE
from upload_r2 import client, BUCKET, CT
UPLOADS = 16   # R2 puts in flight. The client allows 32 connections.

def content_type(path):
    return CT.get(os.path.splitext(path)[1], "application/octet-stream")

def upload_many(s3, pairs):
    """pairs: (local path, key). Sixteen at a time."""
    from concurrent.futures import ThreadPoolExecutor
    if not pairs: return
    def one(pair):
        local, key = pair
        s3.upload_file(local, BUCKET, key, ExtraArgs={"ContentType": content_type(key)})
    with ThreadPoolExecutor(UPLOADS) as ex:
        list(ex.map(one, pairs))

def ready_batch(m, c, hours):
    """10-byte range probe, in order. The first hour that is not out ends the batch, so a hole is not encoded."""
    out = []
    for s in hours:
        if not avail(m, c, s): break
        out.append(s)
    return out

def avail(m, c, s):
    import temp_maps as TM, menu_maps as M
    # 10-31 (Benjamin: "pull ECMWF 9 km 12Z too"): the 9 km source URLs are registered by FE._patch_models, which only ran inside an
    # encode; when the 0.25 deg run was already complete nothing had encoded yet, so every 9 km cycle read as "no cycle out" (the
    # 06Z and 12Z 0.1 deg files were on the source). Register them here so the check sees them.
    FE._patch_models(M)
    try:
        if m in FE.NOAA: u = M.MODELS[m]["url"].format(d=f"{c:%Y%m%d}", h=c.hour, s=s) + ".idx"
        elif m in ("eps", "aens"): u = FE.ENS_SRC[m][0].format(d=f"{c:%Y%m%d}", h=c.hour, s=s) + ".index"
        elif m == "nbm": u = FE.NBM_URL.format(d=f"{c:%Y%m%d}", h=c.hour, s=s) + ".idx"
        elif m == "gfsw": u = FE.WW3_URL.format(d=f"{c:%Y%m%d}", h=c.hour, s=s) + ".idx"   # 11-03 NOAA WaveWatch III (GFS-Wave)
        else: u = TM.MODELS[m]["url"]["sfc"].format(d=f"{c:%Y%m%d}", h=c.hour, s=s) + ".index"
        TM.get(u, (0, 10)); return True
    except Exception: return False

def target_cycle(m):
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    for b in range(0, 36):
        c = now - dt.timedelta(hours=b)
        if c.hour in FE.MODELS[m]["cycles"] and avail(m, c, FE.MODELS[m]["steps"][0]): return c

def cycles_to_encode(newest, stale):
    """Newest source cycle first, then listed cycles whose stored grid is not the current crop."""
    out, seen = [], set()
    for c in ([newest] if newest is not None else []) + list(stale or []):
        if c in seen: continue
        seen.add(c); out.append(c)
    return out

MORE = set(); WORK = {}
LASTMAN = {}
MAN_EVERY = 300   # s between manifest rewrites while a run is coming in (run.json is updated every chunk)
# --watch: minutes after the cycle time when the first step is usually out (measured 10-31 from R2 upload times and the
# NOAA / ECMWF open-data files); watching starts WATCH_EARLY min before that, and stops WATCH_SPAN h after it or when complete
DUE_MIN = {"hrrr": 45, "rrfs": 60, "nbm": 55, "gfs": 200, "ifs": 330, "ifs9": 420, "aifs": 320, "eps": 380, "aens": 350, "gfsw": 215}
WATCH_EARLY, WATCH_SPAN = 60, 6

def run_due(s3, m):
    """True when model m has a cycle whose data is due now (or flowing) and whose run is not complete in R2."""
    now = dt.datetime.now(dt.timezone.utc)
    for b in range(0, 18):
        c = (now - dt.timedelta(hours=b)).replace(minute=0, second=0, microsecond=0)
        if c.hour not in FE.MODELS[m]["cycles"]: continue
        t0 = c + dt.timedelta(minutes=DUE_MIN.get(m, 60))
        if not (t0 - dt.timedelta(minutes=WATCH_EARLY) <= now <= t0 + dt.timedelta(hours=WATCH_SPAN)): continue
        try: r = json.loads(s3.get_object(Bucket=BUCKET, Key=f"runs/{m}/{c:%Y%m%d%H}/run.json")["Body"].read())
        except Exception: return True
        if not r.get("complete"): return True
    return False

def update_manifest(s3, fn, tries=8):
    """Read-modify-write manifest.json with an ETag check (If-Match), so parallel model jobs never overwrite each other.
    A preview publish that had to read the live manifest creates preview/manifest.json (If-None-Match) and does not reuse the live ETag."""
    import random
    for i in range(tries):
        o = s3.get_object(Bucket=BUCKET, Key="manifest.json"); man = json.loads(o["Body"].read()); fn(man)
        kw = dict(Bucket=BUCKET, Key="manifest.json", Body=json.dumps(man).encode(), ContentType="application/json")
        if o.get("_wx_live_fallback"): kw["IfNoneMatch"] = "*"
        else: kw["IfMatch"] = o["ETag"]
        try:
            s3.put_object(**kw)
            try: publish_catalogs(s3, man)
            except Exception as e: print("catalog split:", e, flush=True)
            return man
        except Exception as e:
            if "PreconditionFailed" not in str(e) and "412" not in str(e): raise
            time.sleep(0.5 + random.random() * 2)
    raise SystemExit("manifest.json kept changing; gave up")

def publish_catalogs(s3, man):
    """Slim index plus one complete catalog per model, from the manifest just written. No extra ingest."""
    slim, cats = FE.split_manifest(man)
    s3.put_object(Bucket=BUCKET, Key="manifest.index.json", Body=json.dumps(slim, separators=(",", ":")).encode(), ContentType="application/json")
    for mid, cat in cats.items():
        s3.put_object(Bucket=BUCKET, Key=f"models/{mid}.json", Body=json.dumps(cat, separators=(",", ":")).encode(), ContentType="application/json")

def live_run_ids(s3, model):
    """Cycle ids listed on the live manifest. Empty when this client is not writing under a prefix."""
    if not getattr(s3, "prefix", ""): return []
    try:
        live = json.loads(s3.live_object(Bucket=BUCKET, Key="manifest.json")["Body"].read())
    except Exception as e:
        print("live manifest not read:", e, flush=True); return []
    return list((live.get("runs") or {}).get(model) or [])

def union_live_runs(s3, model, preview_ids, keep):
    """Newest `keep` of the preview cycles plus the cycles still listed on the live manifest."""
    merged = sorted(set(preview_ids) | set(live_run_ids(s3, model)))
    return merged[-keep:] if keep else merged

# Copy a product row from a model that already has it, once a preview run actually encoded the fields.
# Color-key paths are dropped: they name the donor's PNGs, and the viewer skips a missing key.
_GRAFT_EXTRA = {
    "gfs": {"snow": "GFS precip while snow was falling, 10:1  \u00b7  since the run started  \u00b7  max {hi} in in view",
            "ir": "GFS cloud-top temperature, coldest low / middle / high top  \u00b7  2 m temp where clear"},
    "ifs": {"frz": "0\u00b0C height from the model temperature profile  \u00b7  {lo} to {hi} ft in view"},
    "aifs": {"frz": "0\u00b0C height from the model temperature profile  \u00b7  {lo} to {hi} ft in view"},
}
# These products were copied onto GFS and AIFS without a color bar for each view.
_KEY_PRODUCTS = {"refc", "ir", "snow", "frz", "snowlvl"}
_DONORS = ("hrrr", "rrfs", "ifs", "gfs", "aifs")

def ready_fields(steps):
    """Fields present on every published hour.

    A hole in one field drops that field only. refc on all 120 hours still publishes
    when asnow is missing from 118 of them.
    """
    common = None
    for st in steps or []:
        keys = set((st.get("ranges") or {}))
        common = keys if common is None else (common & keys)
    return common or set()

def graft_encoded_products(man, m, fields):
    have = set(fields or [])
    models = man.get("models") or {}
    me = models.get(m)
    if not me or not have: return []
    prods = me.setdefault("products", {})
    added = []
    for pid, allow in FE.PRODUCT_ONLY.items():
        if FE.as_model(m) not in allow or pid in prods: continue
        donor = None
        for other in _DONORS:
            if other == m: continue
            P = ((models.get(other) or {}).get("products") or {}).get(pid)
            need = set((P or {}).get("fields") or [])
            if P and need and need <= have:
                donor = P; break
        if not donor: continue
        copied = json.loads(json.dumps(donor))
        copied.pop("keys", None); copied.pop("only", None); copied.pop("_cm", None)
        extra = (_GRAFT_EXTRA.get(m) or {}).get(pid)
        if extra: copied["extra"] = extra
        if m == "gfs" and pid == "snow": copied["title"] = "Snowfall Total (10:1)"
        prods[pid] = copied
        added.append(pid)
    keyed = ensure_view_keys(me, m)
    if added: print(m, "menu gained", ",".join(added), flush=True)
    if keyed: print(m, "color keys for", ",".join(keyed), flush=True)
    return list(dict.fromkeys(added + keyed))

def ensure_view_keys(model_entry, model):
    """Give refc, ir, snow, and freezing level a color-key path for every view this model publishes."""
    views = list((model_entry.get("views") or {}))
    if not views: return []
    changed = []
    for bucket in ("products", "products_x"):
        for pid, P in (model_entry.get(bucket) or {}).items():
            if pid not in _KEY_PRODUCTS or not isinstance(P, dict): continue
            keys = dict(P.get("keys") or {})
            missing = [vid for vid in views if not keys.get(vid)]
            if not missing: continue
            for vid in missing:
                keys[vid] = FE.product_key(model, pid, vid)
            P["keys"] = keys
            changed.append(pid)
    return changed

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="hrrr,gfs,ifs,aifs"); ap.add_argument("--minutes", type=float, default=40)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--out", default=os.path.join(HERE, "data")); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--watch", action="store_true"); ap.add_argument("--every", type=float, default=60)
    a = ap.parse_args(); t_end = time.time() + a.minutes * 60; D = a.out; os.makedirs(D, exist_ok=True)
    s3 = client(); print("R2 prefix:", getattr(s3, "prefix", "") or "(live)", flush=True)
    s3.download_file(BUCKET, "manifest.json", f"{D}/manifest.json")
    models = a.models.split(",")
    # ECMWF 9 km (ifs9) rides the ECMWF job (no workflow change): after "ifs", once its static layers are in the manifest
    if "ifs" in models and "ifs9" not in models: models.insert(models.index("ifs") + 1, "ifs9")
    # 11-02 (Benjamin 10:32 AM): models listed in env FAST_PAUSED (comma list, set in fast-models.yml) are skipped entirely.
    # ECMWF 9 km is paused: its source kept answering 503 and the ECMWF job hit the 50 min timeout. Re-enable: remove ifs9 there.
    paused = {x.strip() for x in os.environ.get("FAST_PAUSED", "").split(",") if x.strip()}
    if paused & set(models): print("paused (FAST_PAUSED):", sorted(paused & set(models)), flush=True); models = [x for x in models if x not in paused]
    def stale_cycles(m, crop):
        if not crop: return []
        out = []
        listed = (json.load(open(f"{D}/manifest.json")).get("runs") or {}).get(m) or []
        for cyc in listed:
            try: ct = dt.datetime.strptime(cyc, "%Y%m%d%H").replace(tzinfo=dt.timezone.utc)
            except Exception: continue
            try: r = json.loads(s3.get_object(Bucket=BUCKET, Key=f"runs/{m}/{cyc}/run.json")["Body"].read())
            except Exception: continue
            if r and not FE.same_grid(r, crop): out.append(ct)
        return out
    def one(m, c=None):
        if time.time() > t_end - 120: print("time budget used up", flush=True); MORE.add(m); return
        if m not in json.load(open(f"{D}/manifest.json")).get("models", {}): print(m, "no static layers in R2 yet, skipped", flush=True); return
        if c is None: c = target_cycle(m)
        if not c: print(m, "no cycle out", flush=True); return
        cyc = f"{c:%Y%m%d%H}"; key = f"runs/{m}/{cyc}/run.json"; rd = f"{D}/runs/{m}/{cyc}"; os.makedirs(rd + "/single", exist_ok=True)
        crop = (json.load(open(f"{D}/manifest.json")).get("models") or {}).get(m, {}).get("crop")
        try:
            s3.download_file(BUCKET, key, f"{rd}/run.json"); r0 = json.load(open(f"{rd}/run.json"))
            if r0.get("complete") and FE.same_grid(r0, crop): print(m, cyc, "complete in R2", flush=True); return
            if r0 and not FE.same_grid(r0, crop):
                print(m, cyc, "grid", r0.get("grid"), "!= crop", crop, "re-encode", flush=True)
                r0 = None
                try: os.remove(f"{rd}/run.json")
                except OSError: pass
        except Exception: r0 = None
        print(m, cyc, "has", len((r0 or {}).get("steps", [])), "steps in R2", flush=True)
        want = FE.steps_for(m, c.hour)
        # 10-31 frame at a time (Benjamin 11:48 AM "roll hour data one frame at a time the moment the data is available"): a chunk is
        # only as many hours as there are workers, all encoded in parallel, so each chunk takes about one hour's encode time; when
        # the job is caught up with the source only the hours that are out are in the chunk (usually one), and each is uploaded
        # (step files + run.json) as soon as it is encoded, under WX_R2_PREFIX when that is set (preview/ in the workflow).
        # The manifest (run list) is rewritten for a new run, at completion and at
        # most every MAN_EVERY s in between (the viewer follows an open run through its run.json), to keep R2 writes low.
        W = min(a.workers, 2) if m == "ifs9" else a.workers
        chunk = W
        while True:
            if time.time() >= t_end - 60: MORE.add(m); break   # budget ran out with hours left -> ask for a re-dispatch
            have = {x["f"] for x in (json.load(open(f"{rd}/run.json"))["steps"] if os.path.exists(f"{rd}/run.json") else [])}
            nxt = ready_batch(m, c, [s for s in want if s not in have][:chunk])
            if not nxt: break
            first = not (r0 or {}).get("steps")
            def on_prefix(built, fresh):
                files = []
                single = f"{rd}/single"
                if os.path.isdir(single):
                    for fn in os.listdir(single):
                        if any(fn.endswith(f"_f{s:03d}.webp") or fn.endswith(f"_f{s:03d}.png") or fn.endswith(f"_f{s:03d}.json") for s in fresh):
                            files.append(f"runs/{m}/{cyc}/single/{fn}")
                if a.dry_run: return
                upload_many(s3, [(f"{D}/{k_}", k_) for k_ in files])
                s3.upload_file(f"{rd}/run.json", BUCKET, key, ExtraArgs={"ContentType": "application/json"})
                for k_ in files:
                    try: os.remove(f"{D}/{k_}")
                    except OSError: pass
                if first or built["complete"] or time.time() - LASTMAN.get(m, 0) >= MAN_EVERY:
                    publish_manifest(s3, D, m, prog=(cyc, built["steps"][-1]["f"] if built["steps"] else None, want[-1], built["complete"]), fields=ready_fields(built.get("steps"))); LASTMAN[m] = time.time()
                print(f"{m} {cyc}: published F+{fresh[0]}" + (f"–F+{fresh[-1]}" if len(fresh) > 1 else "") + f", {len(built['steps'])}/{len(want)} steps", flush=True)
            run, new = FE.steps(m, cyc, nxt, D, W, on_prefix=None if a.dry_run else on_prefix)
            r0 = run
            if not new: break
            WORK[m] = WORK.get(m, 0) + len(new)
            if run["complete"]:
                if not a.dry_run:
                    try: write_agg(s3, m, cyc, run, f"{rd}/run.json", key)
                    except Exception as e: print(m, cyc, "aggregate town files failed (site falls back to per-step files):", e, flush=True)
                break

    def cycles_for(m):
        crop = (json.load(open(f"{D}/manifest.json")).get("models") or {}).get(m, {}).get("crop")
        return cycles_to_encode(target_cycle(m), stale_cycles(m, crop))
    for m in models:
        for c in cycles_for(m): one(m, c)
    # --watch (10-31): keep polling (every --every s) while a model has a run due or in progress, so a new run starts within
    # about a minute of its first hours being out instead of waiting for the next (throttled, ~40 min apart) cron run
    while a.watch and time.time() < t_end - 180:
        due = [m for m in models if m not in MORE and run_due(s3, m)]
        if not due: print("watch: nothing due, done", flush=True); break
        time.sleep(a.every)
        for m in due:
            for c in cycles_for(m): one(m, c)
    if a.watch:
        for m in models:
            if run_due(s3, m): MORE.add(m)   # still due when the budget ends -> re-dispatch (chains until the run is in)

MG_KEEP = 4   # runs per model with town data for the meteograms page
def write_agg(s3, m, cyc, full, local, key):
    """Complete run -> one single/{pts,mem}_all.json ({"f": [...], "d": [...]}) so a meteogram / the Pass Forecaster
    fetches 1 file instead of ~50. run.json "agg" lists the names; the site falls back to per-step files without it."""
    from concurrent.futures import ThreadPoolExecutor
    agg = []
    for name in ("pts", "mem"):
        fs = [x["f"] for x in full["steps"]]
        def get(f):
            try: return json.loads(s3.get_object(Bucket=BUCKET, Key=f"runs/{m}/{cyc}/single/{name}_f{f:03d}.json")["Body"].read())
            except Exception: return None
        with ThreadPoolExecutor(16) as ex: d = list(ex.map(get, fs))
        if not all(x is not None for x in d): continue
        s3.put_object(Bucket=BUCKET, Key=f"runs/{m}/{cyc}/single/{name}_all.json", Body=json.dumps({"f": fs, "d": d}, separators=(",", ":")).encode(),
                      ContentType="application/json")
        agg.append(name)
    if agg:
        full["agg"] = agg; json.dump(full, open(local, "w"), indent=1)
        s3.upload_file(local, BUCKET, key, ExtraArgs={"ContentType": "application/json"})
        print(m, cyc, "aggregate town files:", agg, flush=True)


def publish_manifest(s3, D, m, prog=None, fields=None):
    keep = FE.MODELS[m]["keep"]
    pre = {o["Prefix"].split("/")[2] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix=f"runs/{m}/", Delimiter="/").get("CommonPrefixes", [])}
    preview_present = sorted(r for r in pre if "Contents" in s3.list_objects_v2(Bucket=BUCKET, Prefix=f"runs/{m}/{r}/run.json", MaxKeys=1))
    # Preview menu keeps cycles that still exist only on the live keys, so the 11-05 run stays listed until newer ones replace it.
    present = sorted(set(preview_present) | set(live_run_ids(s3, m)))
    # 10-31 (keep 2 -> 4): a run already slimmed (map images deleted, marker .../slim) must never come back into the map list
    def is_slim(r):
        try: s3.head_object(Bucket=BUCKET, Key=f"runs/{m}/{r}/slim"); return True
        except Exception: return False
    full = [r for r in present if not is_slim(r)]
    kept = full[-keep:]
    if FE.MODELS[m].get("keep_long"):   # also keep the newest full-length (00/12Z) run so 360 h stays on the site
        longs = [r for r in full if int(r[8:10]) not in FE.MODELS[m].get("short_cycles", ())]
        if longs and longs[-1] not in kept: kept = sorted(kept + [longs[-1]])
    # 10-30 meteograms page multi-run (old site showed 4 runs): the newest MG_KEEP runs keep their small town files
    # (run.json + pts_/mem_ JSON); map images of runs that left the map list are deleted ("slim" runs, marker key .../slim).
    mg = present[-MG_KEEP:]
    # 10-31: runs the box published for the hidden preview before this code was pushed (manifest "runs_x", file run_x.json, so
    # the old workflow never listed them). Once this code runs they are dropped from the manifest and deleted below.
    xr = []
    gained = []
    def both(mn):
        mn.setdefault("runs", {})[m] = kept; mn.setdefault("mgruns", {})[m] = sorted(set(mg) | set(kept))
        # 10-31: runs still coming in -> manifest "progress" {model: {cycle: [last hour live, last hour expected]}} so the site can
        # say "loading" (the production page ignores the key); dropped once complete or out of the list
        pg = mn.setdefault("progress", {}).setdefault(m, {})
        if prog:
            if prog[3]: pg.pop(prog[0], None)
            else: pg[prog[0]] = [prog[1], prog[2]]
        for k in [k for k in pg if k not in kept]: pg.pop(k)
        if not pg: mn["progress"].pop(m)
        xr[:] = (mn.get("runs_x") or {}).pop(m, None) or []
        if "runs_x" in mn and not mn["runs_x"]: del mn["runs_x"]
        gained[:] = graft_encoded_products(mn, m, fields) or []
    man = update_manifest(s3, both)
    if gained:
        me = (man.get("models") or {}).get(m) or {}
        specs = {}
        for pid in gained:
            for bucket in ("products", "products_x"):
                P = (me.get(bucket) or {}).get(pid)
                if isinstance(P, dict) and P.get("keys"): specs[pid] = P
        try:
            paths = FE.write_product_keys(m, specs, D)
        except Exception as e:
            print(m, "color keys not drawn:", e, flush=True); paths = []
        for rel in paths:
            s3.upload_file(f"{D}/{rel}", BUCKET, rel, ExtraArgs={"ContentType": "image/png"})
        if paths: print(m, "uploaded", len(paths), "color keys", flush=True)
    for old in [r for r in xr if r not in present]:
        ks = [o["Key"] for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=f"runs/{m}/{old}/") for o in pg.get("Contents", [])]
        for i in range(0, len(ks), 1000): s3.delete_objects(Bucket=BUCKET, Delete={"Objects": [{"Key": k} for k in ks[i:i + 1000]]})
        print("pruned preview run", m, old, len(ks), "objects", flush=True)
    json.dump(man, open(f"{D}/manifest.json", "w"))
    for old in [r for r in preview_present if r not in kept]:
        slim = old in mg
        if slim:
            try: s3.head_object(Bucket=BUCKET, Key=f"runs/{m}/{old}/slim"); continue   # already slimmed
            except Exception: pass
        ks = [o["Key"] for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=f"runs/{m}/{old}/") for o in pg.get("Contents", [])]
        if slim: ks = [k for k in ks if not (k.endswith("/run.json") or k.split("/")[-1].startswith(("pts_", "mem_")))]
        for i in range(0, len(ks), 1000): s3.delete_objects(Bucket=BUCKET, Delete={"Objects": [{"Key": k} for k in ks[i:i + 1000]]})
        if slim: s3.put_object(Bucket=BUCKET, Key=f"runs/{m}/{old}/slim", Body=b"1")
        print("slimmed" if slim else "pruned", m, old, len(ks), "objects", flush=True)

if __name__ == "__main__":
    main()
    print("more work left:", sorted(MORE) or "none", flush=True)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f: f.write(f"more={'true' if MORE else 'false'}\n")
    sys.stdout.flush(); os._exit(0)
