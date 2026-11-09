"""Preview-first ingest: writes stay under preview/, the menu can gain a product the run actually encoded, and the workflow is scheduled."""
import io, json, os, sys, unittest
from botocore.exceptions import ClientError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

def _miss(op="GetObject"):
    return ClientError({"Error": {"Code": "NoSuchKey", "Message": "no"}}, op)

class FakeRaw:
    def __init__(self):
        self.store = {}
        self.puts = []
        self.deleted = []

    def get_object(self, Bucket, Key, **kw):
        if Key not in self.store: raise _miss()
        body, etag = self.store[Key]
        return {"Body": io.BytesIO(body), "ETag": etag}

    def head_object(self, Bucket, Key, **kw):
        if Key not in self.store: raise _miss("HeadObject")
        return {"ETag": self.store[Key][1]}

    def put_object(self, Bucket, Key, Body, **kw):
        self.puts.append((Key, kw.get("IfMatch"), kw.get("IfNoneMatch")))
        if kw.get("IfNoneMatch") == "*" and Key in self.store:
            raise ClientError({"Error": {"Code": "PreconditionFailed"}}, "PutObject")
        if kw.get("IfMatch") and self.store.get(Key, (None, None))[1] != kw["IfMatch"]:
            raise ClientError({"Error": {"Code": "PreconditionFailed"}}, "PutObject")
        data = Body if isinstance(Body, bytes) else Body.encode()
        etag = "e%d" % len(self.puts)
        self.store[Key] = (data, etag)
        return {"ETag": etag}

    def upload_file(self, Filename, Bucket, Key, **kw):
        self.store[Key] = (open(Filename, "rb").read(), "up")

    def download_file(self, Bucket, Key, Filename, **kw):
        if Key not in self.store: raise _miss()
        open(Filename, "wb").write(self.store[Key][0])

    def delete_object(self, Bucket=None, Key=None, **kw):
        self.deleted.append(Key)
        self.store.pop(Key, None)

    def delete_objects(self, **kw):
        for o in kw["Delete"]["Objects"]:
            self.deleted.append(o["Key"])
            self.store.pop(o["Key"], None)

    def list_objects_v2(self, **kw):
        prefix = kw.get("Prefix", "")
        delim = kw.get("Delimiter")
        keys = [k for k in self.store if k.startswith(prefix)]
        if not delim:
            return {"Contents": [{"Key": k} for k in keys]}
        cps, contents = {}, []
        for k in keys:
            rest = k[len(prefix):]
            if delim in rest: cps[prefix + rest.split(delim)[0] + delim] = 1
            else: contents.append({"Key": k})
        return {"Contents": contents, "CommonPrefixes": [{"Prefix": p} for p in sorted(cps)]}

    def get_paginator(self, name):
        raw = self
        class P:
            def paginate(self, **kw):
                yield raw.list_objects_v2(**kw)
        return P()


class Prefix(unittest.TestCase):
    def setUp(self):
        from upload_r2 import Prefixed
        self.raw = FakeRaw()
        self.s3 = Prefixed(self.raw, "preview/")
        self.raw.store["manifest.json"] = (b'{"runs":{"hrrr":["2026110500"]},"models":{}}', "live")
        self.raw.store["runs/hrrr/2026110500/run.json"] = (b'{"complete":true}', "live-run")
        self.raw.store["preview/runs/hrrr/2026110700/run.json"] = (b'{"complete":false}', "prev")

    def test_writes_and_deletes_stay_under_preview(self):
        self.s3.put_object(Bucket="b", Key="runs/hrrr/2026110700/a.png", Body=b"z")
        self.assertIn("preview/runs/hrrr/2026110700/a.png", self.raw.store)
        self.s3.delete_objects(Bucket="b", Delete={"Objects": [{"Key": "runs/hrrr/2026110500/run.json"}]})
        self.assertIn("runs/hrrr/2026110500/run.json", self.raw.store)
        self.assertEqual(self.raw.deleted, ["preview/runs/hrrr/2026110500/run.json"])

    def test_run_read_does_not_fall_back_to_live(self):
        with self.assertRaises(ClientError):
            self.s3.get_object(Bucket="b", Key="runs/hrrr/2026110500/run.json")
        got = json.loads(self.s3.get_object(Bucket="b", Key="runs/hrrr/2026110700/run.json")["Body"].read())
        self.assertFalse(got["complete"])

    def test_manifest_falls_back_then_creates_preview_copy(self):
        from fast_cycle import update_manifest
        o = self.s3.get_object(Bucket="b", Key="manifest.json")
        self.assertTrue(o.get("_wx_live_fallback"))
        def fn(mn): mn["runs"]["hrrr"] = ["2026110500", "2026110700"]
        update_manifest(self.s3, fn)
        mans = [p for p in self.raw.puts if p[0].endswith("/manifest.json") or p[0] == "manifest.json"]
        self.assertEqual(mans[0][1], None)
        self.assertEqual(mans[0][2], "*")
        self.assertIn("preview/manifest.json", self.raw.store)
        self.assertIn("preview/manifest.index.json", self.raw.store)
        def fn2(mn): mn["runs"]["hrrr"].append("2026110706")
        update_manifest(self.s3, fn2)
        mans = [p for p in self.raw.puts if p[0].endswith("/manifest.json") or p[0] == "manifest.json"]
        self.assertTrue(mans[1][1])
        self.assertIsNone(mans[1][2])
        man = json.loads(self.raw.store["preview/manifest.json"][0])
        self.assertEqual(man["runs"]["hrrr"][-1], "2026110706")
        self.assertIn("2026110500", json.loads(self.raw.store["manifest.json"][0])["runs"]["hrrr"])

    def test_catalogs_follow_the_manifest_on_its_own_prefix(self):
        from upload_r2 import Prefixed
        from fast_cycle import update_manifest
        from promote_preview_to_live import publish_promoted_catalogs
        man = {"runs": {"hrrr": ["2026110718"]}, "models": {
            "hrrr": {"name": "NOAA HRRR", "site": "HRRR", "res": "3 km", "grid": "lcc", "products": {"t2m": {"title": "T"}}},
        }}
        self.raw.store["models/hrrr.json"] = (b'{"name":"STALE"}', "old")
        self.raw.store["manifest.index.json"] = (b'{"catalog_v":0}', "old")
        for prefix in ("preview/", "preview-pr19/"):
            s3 = Prefixed(self.raw, prefix)
            self.raw.store[prefix + "manifest.json"] = (json.dumps({"runs": {}, "models": {}}).encode(), "seed")
            def fn(mn, man=man):
                mn.clear(); mn.update(json.loads(json.dumps(man)))
            update_manifest(s3, fn)
            self.assertIn(prefix + "manifest.index.json", self.raw.store)
            cat = json.loads(self.raw.store[prefix + "models/hrrr.json"][0])
            self.assertEqual(cat["name"], "NOAA HRRR")
            self.assertEqual(cat["products"]["t2m"]["title"], "T")
            idx = json.loads(self.raw.store[prefix + "manifest.index.json"][0])
            self.assertEqual(idx["catalog_v"], 1)
            self.assertEqual(idx["models"]["hrrr"]["catalog"], "models/hrrr.json")
            self.assertNotIn("products", idx["models"]["hrrr"])
        self.assertEqual(json.loads(self.raw.store["models/hrrr.json"][0])["name"], "STALE")
        self.assertIn("preview/models/hrrr.json", self.raw.store)
        self.raw.store["manifest.json"] = (json.dumps(man).encode(), "live")
        publish_promoted_catalogs(self.raw, "b")
        self.assertEqual(json.loads(self.raw.store["models/hrrr.json"][0])["name"], "NOAA HRRR")
        self.assertEqual(json.loads(self.raw.store["manifest.index.json"][0])["catalog_v"], 1)
        self.assertEqual(json.loads(self.raw.store["preview-pr19/models/hrrr.json"][0])["name"], "NOAA HRRR")

    def test_list_strips_prefix_for_cycle_ids(self):
        page = self.s3.list_objects_v2(Bucket="b", Prefix="runs/hrrr/", Delimiter="/")
        self.assertEqual([o["Prefix"].split("/")[2] for o in page["CommonPrefixes"]], ["2026110700"])

    def test_paginator_strips_prefix(self):
        keys = [o["Key"] for pg in self.s3.get_paginator("list_objects_v2").paginate(Bucket="b", Prefix="runs/hrrr/2026110700/") for o in pg.get("Contents", [])]
        self.assertEqual(keys, ["runs/hrrr/2026110700/run.json"])

    def test_deployment_prefix_does_not_write_the_shared_preview(self):
        from upload_r2 import Prefixed, normalize_prefix
        self.assertEqual(normalize_prefix("preview-pr16"), "preview-pr16/")
        self.assertEqual(normalize_prefix("preview/"), "preview/")
        self.assertEqual(normalize_prefix(""), "")
        with self.assertRaises(SystemExit):
            normalize_prefix("runs/")
        iso = Prefixed(self.raw, normalize_prefix("preview-pr16"))
        iso.put_object(Bucket="b", Key="runs/hrrr/2026110712/a.png", Body=b"z")
        self.assertIn("preview-pr16/runs/hrrr/2026110712/a.png", self.raw.store)
        self.assertNotIn("preview/runs/hrrr/2026110712/a.png", self.raw.store)
        self.assertNotIn("runs/hrrr/2026110712/a.png", self.raw.store)


class Graft(unittest.TestCase):
    def test_gfs_and_aifs_gain_products_the_run_encoded(self):
        from fast_cycle import graft_encoded_products
        man = {"models": {
            "hrrr": {"products": {
                "refc": {"title": "Radar", "fields": ["refc"], "keys": {"pnwhr": "static/key_hrrr.png"}},
                "ir": {"title": "IR", "fields": ["ir"], "keys": {"wa": "static/key_hrrr_ir.png"}},
                "snow": {"title": "Snow", "fields": ["asnow"], "extra": "HRRR snowfall", "keys": {"wa": "k"}},
            }},
            "gfs": {"views": {"na": {}, "pac": {}, "pnwwide": {}}, "products": {"t2m": {"fields": ["t2m"]}}},
            "ifs": {"products": {"frz": {"title": "Freezing Level", "fields": ["frz"], "keys": {"na": "k"}}}},
            "aifs": {"views": {"na": {}, "pnwhr": {}}, "products": {}},
        }}
        added = graft_encoded_products(man, "gfs", ["t2m", "refc", "asnow"])
        self.assertEqual(added, ["refc", "snow"])
        keys = man["models"]["gfs"]["products"]["refc"]["keys"]
        self.assertEqual(set(keys), {"na", "pac", "pnwwide"})
        self.assertEqual(keys["pnwwide"], "static/key_gfs_refc_pnwwide.png")
        self.assertEqual(set(man["models"]["gfs"]["products"]["snow"]["keys"]), {"na", "pac", "pnwwide"})
        self.assertIn("10:1", man["models"]["gfs"]["products"]["snow"]["extra"])
        self.assertNotIn("ir", man["models"]["gfs"]["products"])
        added = graft_encoded_products(man, "aifs", ["frz"])
        self.assertEqual(added, ["frz"])
        self.assertIn("profile", man["models"]["aifs"]["products"]["frz"]["extra"])
        self.assertEqual(set(man["models"]["aifs"]["products"]["frz"]["keys"]), {"na", "pnwhr"})
        self.assertEqual(graft_encoded_products(man, "gfs", ["t2m", "refc", "asnow"]), [])

    def test_a_missing_field_blocks_only_that_field(self):
        from fast_cycle import graft_encoded_products, ready_fields
        steps = []
        for f in range(3, 363, 3):
            ranges = {"t2m": [0, 1], "refc": [0, 1], "ir": [0, 1]}
            if f in (3, 6):
                ranges["asnow"] = [0, 1]
            steps.append({"f": f, "ranges": ranges})
        ready = ready_fields(steps)
        self.assertEqual(ready, {"t2m", "refc", "ir"})
        man = {"models": {
            "hrrr": {"products": {
                "refc": {"title": "Radar", "fields": ["refc"], "keys": {"na": "k"}},
                "ir": {"title": "IR", "fields": ["ir"], "keys": {"na": "k"}},
                "snow": {"title": "Snow", "fields": ["asnow"], "keys": {"na": "k"}},
            }},
            "gfs": {"views": {"na": {}, "pac": {}}, "products": {}},
        }}
        added = graft_encoded_products(man, "gfs", ready)
        self.assertEqual(set(added), {"refc", "ir"})
        self.assertNotIn("snow", man["models"]["gfs"]["products"])
        for st in steps:
            st["ranges"]["asnow"] = [0, 1]
        self.assertIn("asnow", ready_fields(steps))
        self.assertIn("snow", graft_encoded_products(man, "gfs", ready_fields(steps)))

    def test_aifs_frz_skips_a_missing_level(self):
        import numpy as np
        import fast_encode as FE
        class R:
            def f(self, name):
                if name == "T:925" or name == "Z:925": raise KeyError(name)
                if name.startswith("T:"):
                    lev = int(name.split(":")[1])
                    return (None, None, np.array([280.0 if lev >= 1000 else 260.0]))
                if name.startswith("Z:"):
                    lev = int(name.split(":")[1])
                    return (None, None, np.array([{1000: 100.0, 850: 1500.0}.get(lev, 4000.0)]))
                if name == "sp": return (None, None, np.array([101325.0]))
                raise KeyError(name)
        z = FE._frz(R(), "aifs")
        self.assertTrue(np.isfinite(z).all())
        self.assertGreater(float(z[0]), 100 * 3.28084)
        self.assertLess(float(z[0]), 1500 * 3.28084)
        class One:
            def f(self, name):
                if name in ("T:1000", "Z:1000"): return (None, None, np.array([280.0 if name.startswith("T") else 100.0]))
                raise KeyError(name)
        with self.assertRaises(KeyError):
            FE._frz(One(), "aifs")


class Workflow(unittest.TestCase):
    def test_schedule_checkout_and_preview_switch(self):
        with open(os.path.join(ROOT, ".github", "workflows", "fast-models.yml"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("FAST_PAUSED", text)
        self.assertNotIn("sparse-checkout", text)
        self.assertIn('cron: "7,22,37,52 * * * *"', text)
        self.assertNotIn("#   - cron:", text)
        self.assertIn("inputs.prefix || 'preview/'", text)
        self.assertIn('default: "preview/"', text)
        self.assertIn("preview-pr16/", text)
        self.assertIn("PNW_R2_ACCESS_KEY_ID", text)
        self.assertIn("PNW_R2_SECRET_ACCESS_KEY", text)
        self.assertNotIn("CF_PAGES_KEY", text)
        self.assertIn("promote_preview_to_live.py", text)
        self.assertIn("regions/stations.json", text)
        self.assertIn("frame_scheduler.py", text)
        self.assertIn("--poll 45", text)
        self.assertIn('-f prefix="${{ inputs.prefix || \'preview/\' }}"', text)


if __name__ == "__main__":
    unittest.main()
