#!/usr/bin/env python3
"""Promote R2 keys from preview/ to live (no prefix). PNW account + pnw-models-data only.
Does NOT overwrite an existing live object unless the key is manifest.json or ends with /run.json
(those are backed up first under backups/prod_promote_YYYYMMDD/ when --backup-dir is set).
After the live manifest is replaced, its index and catalogs are written on the live keys.
usage: python3 promote_preview_to_live.py [--backup-dir DIR] [--dry-run]"""
import os, sys, json, boto3
from concurrent.futures import ThreadPoolExecutor, as_completed
A = "b6dc205037fd8e8c37d5267ee61dc302"
B = "pnw-models-data"

def publish_promoted_catalogs(s3, bucket=B):
    """The live manifest was just replaced. Rewrite the live index and catalogs from it."""
    from fast_cycle import publish_catalogs
    man = json.loads(s3.get_object(Bucket=bucket, Key="manifest.json")["Body"].read())
    publish_catalogs(s3, man)
    print("live catalogs published from manifest.json", flush=True)
    return man

def main():
    DRY = "--dry-run" in sys.argv
    BD = None
    if "--backup-dir" in sys.argv:
        BD = sys.argv[sys.argv.index("--backup-dir") + 1]
    s3 = boto3.client("s3", endpoint_url=f"https://{A}.r2.cloudflarestorage.com", region_name="auto",
                      aws_access_key_id=os.environ["PNW_R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["PNW_R2_SECRET_ACCESS_KEY"])
    # Inventory
    live, prev = {}, {}
    for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=B):
        for o in pg.get("Contents", []):
            k = o["Key"]
            # preview-pr16/ and the other per-deployment prefixes stay where they are.
            if k.startswith("preview-"): continue
            if k.startswith("preview/"):
                prev[k[len("preview/"):]] = o
            else:
                live[k] = o
    print(f"preview_objects={len(prev)} live_objects={len(live)}")
    # Backup live manifest (+ run.jsons we will overwrite)
    os.makedirs(BD or "/tmp/promote_bak", exist_ok=True)
    bak = BD or "/tmp/promote_bak"
    if "manifest.json" in live and not DRY:
        s3.download_file(B, "manifest.json", os.path.join(bak, "manifest.live.before.json"))
        print("backed up manifest.live.before.json")

    def should_write(live_key):
        if live_key not in live:
            return "new"
        base = live_key.split("/")[-1]
        if live_key == "manifest.json" or base == "run.json":
            return "replace_index"
        return None

    todo = []
    for lk, meta in prev.items():
        reason = should_write(lk)
        if reason:
            todo.append((lk, reason, meta["Size"]))

    print(f"to_promote={len(todo)} (new={sum(1 for _,r,_ in todo if r=='new')} replace_index={sum(1 for _,r,_ in todo if r=='replace_index')})")
    # Backup run.jsons being replaced
    n_bak = 0
    if not DRY:
        for lk, reason, _ in todo:
            if reason == "replace_index" and lk != "manifest.json" and lk in live:
                safe = lk.replace("/", "__")
                s3.download_file(B, lk, os.path.join(bak, safe))
                n_bak += 1
        print(f"backed_up_index_files={n_bak}")

    def copy_one(lk):
        src = {"Bucket": B, "Key": "preview/" + lk}
        s3.copy_object(Bucket=B, Key=lk, CopySource=src)
        return lk

    if DRY:
        print("DRY RUN — no copies")
        for lk, r, sz in sorted(todo)[:20]:
            print(" ", r, lk, sz)
        print(" ..." if len(todo) > 20 else "")
        if any(lk == "manifest.json" for lk, _, _ in todo):
            print("would publish live catalogs from manifest.json")
        return 0

    ok = err = 0
    copied = set()
    with ThreadPoolExecutor(24) as ex:
        futs = {ex.submit(copy_one, lk): lk for lk, _, _ in todo}
        for f in as_completed(futs):
            try:
                copied.add(f.result()); ok += 1
                if ok % 200 == 0: print(f"  copied {ok}/{len(todo)}", flush=True)
            except Exception as e:
                err += 1
                print("ERR", futs[f], type(e).__name__, str(e)[:120], flush=True)
    if "manifest.json" in copied:
        publish_promoted_catalogs(s3, B)
    print(f"PROMOTE_DONE ok={ok} err={err}")
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
