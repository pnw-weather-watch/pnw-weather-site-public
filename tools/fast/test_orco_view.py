"""Oregon & Coast: the whole state, coast near the middle, true Lambert shape."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import camera as CAM
import house_style as HS
from test_browser_layers import view_of

REGIONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))


class OrcoView(unittest.TestCase):
    def setUp(self):
        import json
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["orco"]

    def test_label_and_lambert_window_cover_oregon(self):
        self.assertEqual(self.v["label"], "Oregon & Coast")
        self.assertEqual(self.v["proj"][0], "lcc")
        self.assertEqual(self.v["proj"][1], -124.2)
        w, e, s, n = self.v["ll"]
        self.assertGreater(e, -116.4)       # the east edge is past the Idaho border
        self.assertLess(w, -128)            # open ocean on the west
        self.assertLess(s, 42.0)
        self.assertGreater(n, 46.3)
        cam = CAM.Camera(view_of("orco"))
        try:
            px, py, pw, ph = cam.panel()
            x, y = cam.pixel(-124.2, 44.2)
            self.assertAlmostEqual(x, px + pw / 2, delta=pw * 0.04)
            for name, lat, lon in (
                ("Astoria", 46.19, -123.83),
                ("Brookings", 42.05, -124.28),
                ("Ontario", 44.03, -116.96),
                ("Bend", 44.06, -121.31),
            ):
                xx, yy = cam.pixel(lon, lat)
                self.assertTrue(px + 30 < xx < px + pw - 30 and py + 30 < yy < py + ph - 30, name)
            x0, y0 = cam.pixel(-121.3, 44.0)
            x1, y1 = cam.pixel(-121.3, 45.0)
            x2, y2 = cam.pixel(-120.3, 44.0)
            dlat = math.hypot(x1 - x0, y1 - y0)
            dlon = math.hypot(x2 - x0, y2 - y0)
            self.assertAlmostEqual(dlon / (dlat * math.cos(math.radians(44.0))), 1.0, delta=0.02)
            dx = abs(cam.xlim[1] - cam.xlim[0])
            dy = abs(cam.ylim[1] - cam.ylim[0])
            slot = HS.screen_layout(cam.fig)["axes"]
            aspect = (slot[2] * HS.SCREEN_IN[0]) / (slot[3] * HS.SCREEN_IN[1])
            self.assertAlmostEqual(dx / dy, aspect, delta=0.02)
        finally:
            cam.close()

    def test_every_model_that_lists_views_includes_orco(self):
        missing = [m for m, vs in self.R["model_views"].items() if "orco" not in vs]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
