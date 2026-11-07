#!/usr/bin/env python3
"""Upload fast-style data to R2 bucket pnw-models-data (S3 API; PNW R2 keys from env PNW_R2_ACCESS_KEY_ID / PNW_R2_SECRET_ACCESS_KEY, account pinned).
  upload_r2.py --data <site/data> [--run 2026102918] [--static] [--keep 2] [--dry-run]
Order: static (if asked) -> run files -> run.json -> manifest (lists only runs present in R2, newest --keep) -> prune older runs."""
import os, sys, json, hashlib, argparse, urllib.request, mimetypes, time, re
from concurrent.futures import ThreadPoolExecutor
import boto3
from botocore.config import Config
BUCKET = os.environ.get("R2_BUCKET", "pnw-models-data")
CT = {".png": "image/png", ".json": "application/json", ".bin": "application/octet-stream", ".webp": "image/webp"}
_PREFIX = re.compile(r"preview(-[a-z0-9][a-z0-9-]*)?/")

def normalize_prefix(raw):
    """preview/ or preview-<name>/ (preview-pr16/). Empty means the live keys."""
    pre = (raw or "").strip()
    if not pre: return ""
    if not pre.endswith("/"): pre += "/"
    if not _PREFIX.fullmatch(pre):
        raise SystemExit(f"WX_R2_PREFIX must be preview/ or preview-<name>/, not {raw!r}")
    return pre

def client():
    # 11-04 safety: pinned to the PNW account (b6dc...) and the PNW R2 S3 keys; the shared CF_PAGES_KEY / CLOUDFLARE_ACCOUNT_ID belong to the OTHER site and are never read.
    # WX_R2_PREFIX (the ingest workflow sets preview/) sends every write under that prefix. manifest.json and static/ reads
    # fall back to the live key so the first preview cycle can see the current manifest. runs/ reads do not fall back, so a
    # finished live cycle is not treated as already published. Deletes stay under the prefix.
    acc = "b6dc205037fd8e8c37d5267ee61dc302"
    raw = boto3.client("s3", endpoint_url=f"https://{acc}.r2.cloudflarestorage.com", aws_access_key_id=os.environ["PNW_R2_ACCESS_KEY_ID"],
                       aws_secret_access_key=os.environ["PNW_R2_SECRET_ACCESS_KEY"], region_name="auto",
                       config=Config(max_pool_connections=32, retries={"max_attempts": 5, "mode": "standard"}))
    pre = normalize_prefix(os.environ.get("WX_R2_PREFIX", ""))
    return Prefixed(raw, pre) if pre else raw


class Prefixed:
    """S3 client that writes under prefix and strips it on the way back out."""

    def __init__(self, raw, prefix):
        self.raw = raw
        self.prefix = prefix or ""

    def _k(self, key):
        if not self.prefix or key.startswith(self.prefix): return key
        return self.prefix + key

    def _run_key(self, key):
        return key.startswith("runs/")

    def _missing(self, err):
        from botocore.exceptions import ClientError
        if not isinstance(err, ClientError): return False
        return str(err.response.get("Error", {}).get("Code", "")) in ("NoSuchKey", "404", "NotFound")

    def _strip_page(self, page):
        n = len(self.prefix)
        for o in page.get("Contents") or []:
            if o.get("Key", "").startswith(self.prefix): o["Key"] = o["Key"][n:]
        for o in page.get("CommonPrefixes") or []:
            if o.get("Prefix", "").startswith(self.prefix): o["Prefix"] = o["Prefix"][n:]
        return page

    def get_object(self, **kw):
        key = kw["Key"]
        if not self.prefix: return self.raw.get_object(**kw)
        try:
            o = self.raw.get_object(**{**kw, "Key": self._k(key)})
            o["_wx_preview"] = True
            return o
        except Exception as e:
            if self._run_key(key) or not self._missing(e): raise
            o = self.raw.get_object(**kw)
            o["_wx_live_fallback"] = True
            return o

    def head_object(self, **kw):
        key = kw["Key"]
        if not self.prefix: return self.raw.head_object(**kw)
        try:
            return self.raw.head_object(**{**kw, "Key": self._k(key)})
        except Exception as e:
            if self._run_key(key) or not self._missing(e): raise
            return self.raw.head_object(**kw)

    def put_object(self, **kw):
        kw = dict(kw); kw["Key"] = self._k(kw["Key"])
        return self.raw.put_object(**kw)

    def upload_file(self, Filename, Bucket, Key, **kw):
        return self.raw.upload_file(Filename, Bucket, self._k(Key), **kw)

    def download_file(self, Bucket, Key, Filename, **kw):
        try:
            return self.raw.download_file(Bucket, self._k(Key), Filename, **kw)
        except Exception as e:
            if not self.prefix or self._run_key(Key) or not self._missing(e): raise
            return self.raw.download_file(Bucket, Key, Filename, **kw)

    def delete_object(self, **kw):
        kw = dict(kw); kw["Key"] = self._k(kw["Key"])
        return self.raw.delete_object(**kw)

    def delete_objects(self, **kw):
        kw = dict(kw)
        delete = dict(kw.get("Delete") or {})
        delete["Objects"] = [{"Key": self._k(o["Key"])} for o in (delete.get("Objects") or [])]
        kw["Delete"] = delete
        return self.raw.delete_objects(**kw)

    def list_objects_v2(self, **kw):
        kw = dict(kw)
        kw["Prefix"] = self._k(kw.get("Prefix", ""))
        return self._strip_page(self.raw.list_objects_v2(**kw))

    def get_paginator(self, name):
        if name != "list_objects_v2" or not self.prefix: return self.raw.get_paginator(name)
        raw_p = self.raw.get_paginator(name)
        outer = self
        class P:
            def paginate(self, **kw):
                kw = dict(kw)
                kw["Prefix"] = outer._k(kw.get("Prefix", ""))
                for page in raw_p.paginate(**kw):
                    yield outer._strip_page(page)
        return P()

    def live_object(self, **kw):
        """Read the unprefixed key. The preview manifest uses this to keep cycles that still live only on the live keys."""
        return self.raw.get_object(**kw)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--static", action="store_true"); ap.add_argument("--keep", type=int, default=2); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="hrrr"); a = ap.parse_args(); D = a.data.rstrip("/")
    s3 = None if a.dry_run else client(); t0 = time.time(); n = [0, 0]
    def put(rel, cache=None):
        p = f"{D}/{rel}"; n[0] += 1; n[1] += os.path.getsize(p)
        if a.dry_run: return
        s3.upload_file(p, BUCKET, rel, ExtraArgs={"ContentType": CT.get(os.path.splitext(p)[1], "application/octet-stream")})
    files = []
    if a.static: files += [os.path.relpath(os.path.join(r, f), D) for r, _, n in os.walk(f"{D}/static") for f in sorted(n)]   # incl. static/x2/
    for r in a.run:
        rd = f"runs/{a.model}/{r}"; files += [f"{rd}/single/{f}" for f in sorted(os.listdir(f"{D}/{rd}/single")) if f.endswith(".png")]
    with ThreadPoolExecutor(16) as ex: list(ex.map(put, files))
    for r in a.run: put(f"runs/{a.model}/{r}/run.json")
    # manifest: runs = those whose run.json is in R2 (or local in dry run), newest --keep
    if a.dry_run: present = sorted(a.run)
    else:
        present = sorted({o["Prefix"].split("/")[2] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix=f"runs/{a.model}/", Delimiter="/").get("CommonPrefixes", [])})
        present = [r for r in present if "Contents" in s3.list_objects_v2(Bucket=BUCKET, Prefix=f"runs/{a.model}/{r}/run.json", MaxKeys=1)]
    keep = present[-a.keep:]; man = json.load(open(f"{D}/manifest.json")); man.setdefault("runs", {})[a.model] = keep
    if not a.dry_run:
        s3.put_object(Bucket=BUCKET, Key="manifest.json", Body=json.dumps(man).encode(), ContentType="application/json")
        for old in present[:-a.keep]:   # prune (the lifecycle rule also expires runs/ after 3 days)
            ks = [o["Key"] for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=f"runs/{a.model}/{old}/") for o in pg.get("Contents", [])]
            for i in range(0, len(ks), 1000): s3.delete_objects(Bucket=BUCKET, Delete={"Objects": [{"Key": k} for k in ks[i:i + 1000]]})
            print("pruned", old, len(ks), "objects")
    print(f"{'DRY RUN ' if a.dry_run else ''}uploaded {n[0]} files, {n[1]/1e6:.1f} MB in {time.time()-t0:.1f} s; manifest runs {keep}")
if __name__ == "__main__": main()
