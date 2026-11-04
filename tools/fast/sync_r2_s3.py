#!/usr/bin/env python3
"""Sync a local data dir to R2 bucket pnw-models-data with the R2 S3 token (env PNW_R2_ACCESS_KEY_ID / PNW_R2_SECRET_ACCESS_KEY,
CLOUDFLARE_ACCOUNT_ID). Keys = paths relative to the data dir (what /d/<key> serves). Skips objects with the same size and MD5.
usage: python3 sync_r2_s3.py DATA_DIR"""
import os, sys, mimetypes, hashlib, boto3
from concurrent.futures import ThreadPoolExecutor
D = sys.argv[1].rstrip("/"); A = "b6dc205037fd8e8c37d5267ee61dc302"   # pinned: PNW account only (shared env CLOUDFLARE_ACCOUNT_ID is the other site)
s3 = boto3.client("s3", endpoint_url=f"https://{A}.r2.cloudflarestorage.com", region_name="auto",
                  aws_access_key_id=os.environ["PNW_R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["PNW_R2_SECRET_ACCESS_KEY"])
B = "pnw-models-data"; have = {}
for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=B):
    for o in pg.get("Contents", []): have[o["Key"]] = (o["Size"], o["ETag"].strip('"'))
todo = [(os.path.join(r, f), os.path.relpath(os.path.join(r, f), D)) for r, _, fs in os.walk(D) for f in fs]
def same(p, k):
    h = have.get(k)
    if not h or h[0] != os.path.getsize(p): return False
    return "-" in h[1] or hashlib.md5(open(p, "rb").read()).hexdigest() == h[1]   # multipart ETag: size match only
todo = [(p, k) for p, k in todo if not same(p, k)]
todo.sort(key=lambda t: t[1].endswith("manifest.json"))   # manifest last
def put(t):
    p, k = t; ct = mimetypes.guess_type(p)[0] or "application/octet-stream"
    s3.upload_file(p, B, k, ExtraArgs={"ContentType": ct}); return k
with ThreadPoolExecutor(16) as ex: n = sum(1 for _ in ex.map(put, [t for t in todo if not t[1].endswith("manifest.json")]))
for t in todo:
    if t[1].endswith("manifest.json"): put(t); n += 1
print(f"uploaded {n} files, {len(have)} already there")
