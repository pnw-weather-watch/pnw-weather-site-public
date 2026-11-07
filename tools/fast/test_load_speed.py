"""Frame codec, manifest split, and gap-free hour publishing."""
import gzip
import io
import json
import os
import unittest

import numpy as np
from PIL import Image

import fast_encode as fe


class Frames(unittest.TestCase):
    def test_lossless_webp_matches_png_pixels_and_is_smaller(self):
        rng = np.random.default_rng(1)
        h, w = 180, 240
        base = np.linspace(0, 255, w, dtype=np.float32)
        img = np.clip(base[None, :] + np.linspace(0, 30, h, dtype=np.float32)[:, None] + rng.normal(0, 2, size=(h, w)), 0, 255).astype(np.uint8)
        rgb = np.stack([img, (img // 2), (255 - img)], -1)
        im = Image.fromarray(rgb, "RGB")
        png, webp = io.BytesIO(), io.BytesIO()
        im.save(png, format="PNG", optimize=True)
        im.save(webp, format="WEBP", lossless=True, quality=100, method=4)
        back = np.asarray(Image.open(io.BytesIO(webp.getvalue())).convert("RGB"))
        self.assertTrue(np.array_equal(back, rgb))
        self.assertLess(webp.tell(), png.tell())

    def test_split_manifest_keeps_the_catalog_and_gzip_shrinks_it(self):
        town = {"name": "Seattle", "lat": 47.6, "lon": -122.3, "fi": 1, "fj": 2, "x": 0.1, "y": 0.2}
        views = {f"v{i}": {"label": f"View {i}", "towns": [dict(town, name=f"T{i}-{k}") for k in range(40)]} for i in range(12)}
        products = {f"p{i}": {"title": f"Product {i}", "levels": list(range(30)), "colors": ["#112233"] * 29} for i in range(8)}
        man = {"static_v": "t", "runs": {"hrrr": ["2026110718"]}, "models": {
            "hrrr": {"name": "NOAA HRRR", "site": "HRRR", "res": "3 km", "grid": "lcc", "views": views, "products": products, "crop": [0, 10, 0, 10]},
            "gfs": {"name": "NOAA GFS", "site": "GFS", "res": "0.25", "grid": "ll", "views": views, "products": products},
        }}
        raw = json.dumps(man).encode()
        slim, cats = fe.split_manifest(man)
        self.assertEqual(slim["catalog_v"], 1)
        self.assertNotIn("products", slim["models"]["hrrr"])
        self.assertEqual(slim["models"]["hrrr"]["catalog"], "models/hrrr.json")
        self.assertIn("products", cats["hrrr"])
        self.assertEqual(cats["hrrr"]["crop"], [0, 10, 0, 10])
        one = json.dumps(slim).encode() + json.dumps(cats["hrrr"]).encode()
        self.assertLess(len(one), len(raw))
        gz = gzip.compress(raw, 6)
        self.assertLess(len(gz), len(raw) * 0.5)

    def test_contiguous_prefix_stops_at_the_first_hole(self):
        self.assertEqual(fe.contiguous_prefix([1, 2, 3, 4], {1, 2, 4}), [1, 2])
        self.assertEqual(fe.contiguous_prefix([3, 6, 9], {3, 6}), [3, 6])
        self.assertEqual(fe.contiguous_prefix([1, 2], set()), [])


class CachePolicy(unittest.TestCase):
    def test_function_keeps_the_immutable_frame_cache_and_the_short_manifest_cache(self):
        src = open(os.path.join(os.path.dirname(__file__), "functions", "d", "[[path]].js"), encoding="utf-8").read()
        self.assertIn("private, max-age=30", src)
        self.assertIn("private, max-age=31536000, immutable", src)
        self.assertIn("content-encoding", src)
        self.assertIn("100,000", src)


if __name__ == "__main__":
    unittest.main()
