"""California Passes: renamed label, I-5 Black Butte Summit, north edge past Mount Shasta."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import camera as CAM
from test_browser_layers import view_of

REGIONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))


class CapassesView(unittest.TestCase):
    def setUp(self):
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["capasses"]
        self.passes = self.R["CA_PASSES"]

    def test_label_is_california_passes(self):
        self.assertEqual(self.v["label"], "California Passes")
        self.assertNotIn("Sierra", self.v["label"])

    def test_black_butte_summit_is_the_i5_gap(self):
        p = self.passes["Black Butte Summit"]
        self.assertEqual(p["label"], "Black Butte")
        self.assertEqual(p["route"], "I-5")
        self.assertEqual(p["elev_ft"], 3912)
        self.assertAlmostEqual(p["lat"], 41.3546, places=4)
        self.assertAlmostEqual(p["lon"], -122.3539, places=4)
        self.assertIn("1657848", p["src"])

    def test_frame_reaches_shasta_and_keeps_tejon(self):
        self.assertEqual(self.v["proj"][0], "lcc")
        self.assertIn("extent", self.v)
        import math
        cam = CAM.Camera(view_of("capasses"))
        try:
            px, py, pw, ph = cam.panel()
            for key in self.passes:
                p = self.passes[key]
                x, y = cam.pixel(p["lon"], p["lat"])
                self.assertTrue(px + 40 < x < px + pw - 40 and py + 40 < y < py + ph - 40, p["label"])
            x0, y0 = cam.pixel(-120.6, 38.0)
            x1, y1 = cam.pixel(-120.6, 39.0)
            x2, y2 = cam.pixel(-119.6, 38.0)
            dlat = math.hypot(x1 - x0, y1 - y0)
            dlon = math.hypot(x2 - x0, y2 - y0)
            self.assertAlmostEqual(dlon / (dlat * math.cos(math.radians(38.0))), 1.0, delta=0.02)
        finally:
            cam.close()

    def test_models_that_draw_california_passes_still_list_it(self):
        have = [m for m, vs in self.R["model_views"].items() if "capasses" in vs]
        self.assertEqual(have, ["hrrr", "rrfs", "nbm", "gfs", "ifs", "ifs9"])


if __name__ == "__main__":
    unittest.main()
