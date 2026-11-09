"""Washington: the whole state, true Lambert shape, a small bit of BC/OR/Idaho."""
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


# Corners and well-known places that must sit inside the map panel.
WA_PLACES = (
    ("Neah Bay", 48.3681, -124.6150),
    ("Cape Disappointment", 46.2758, -124.0522),
    ("Vancouver WA", 45.6387, -122.6615),
    ("Walla Walla", 46.0646, -118.3430),
    ("Pullman", 46.7298, -117.1817),
    ("Spokane", 47.6588, -117.4260),
    ("Oroville", 48.9388, -119.4356),
    ("Seattle", 47.6062, -122.3321),
    ("Yakima", 46.6021, -120.5059),
)


class WaView(unittest.TestCase):
    def setUp(self):
        import json
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["wa"]

    def test_label_and_lambert_window_cover_washington(self):
        self.assertEqual(self.v["label"], "Washington")
        self.assertEqual(self.v["proj"][0], "lcc")
        w, e, s, n = self.v["ll"]
        self.assertLess(w, -124.8)          # west of Cape Flattery / a bit of ocean
        self.assertGreater(e, -116.9)       # past the Idaho border
        self.assertLess(s, 45.54)           # a bit of Oregon
        self.assertGreater(n, 49.0)         # a bit of British Columbia
        cam = CAM.Camera(view_of("wa"))
        try:
            px, py, pw, ph = cam.panel()
            for name, lat, lon in WA_PLACES:
                xx, yy = cam.pixel(lon, lat)
                self.assertTrue(
                    px + 30 < xx < px + pw - 30 and py + 30 < yy < py + ph - 30,
                    f"{name} at ({xx:.1f},{yy:.1f}) not inside panel {px,py,pw,ph}",
                )
            # True shape: 1 deg lon vs 1 deg lat at mid-latitude matches cosine.
            x0, y0 = cam.pixel(-120.5, 47.4)
            x1, y1 = cam.pixel(-120.5, 48.4)
            x2, y2 = cam.pixel(-119.5, 47.4)
            dlat = math.hypot(x1 - x0, y1 - y0)
            dlon = math.hypot(x2 - x0, y2 - y0)
            self.assertAlmostEqual(dlon / (dlat * math.cos(math.radians(47.4))), 1.0, delta=0.02)
            dx = abs(cam.xlim[1] - cam.xlim[0])
            dy = abs(cam.ylim[1] - cam.ylim[0])
            slot = HS.screen_layout(cam.fig)["axes"]
            aspect = (slot[2] * HS.SCREEN_IN[0]) / (slot[3] * HS.SCREEN_IN[1])
            self.assertAlmostEqual(dx / dy, aspect, delta=0.02)
        finally:
            cam.close()

    def test_every_model_that_lists_views_includes_wa(self):
        missing = [m for m, vs in self.R["model_views"].items() if "wa" not in vs]
        self.assertEqual(missing, [])

    def test_town_names_use_the_tight_approved_scale(self):
        self.assertIn("wa", HS.GLOBAL_PNW_VIEWS)
        self.assertNotIn("wa", HS.WIDE_PNW_VIEWS)
        sc = HS.town_scale_for("gfs", "wa")
        self.assertEqual(sc, HS.GLOBAL_PNW_TOWN_SCALE)
        self.assertEqual(sc, {1: 0.54, 2: 0.72, 3: 0.82})
        self.assertTrue(HS.small_towns("hrrr", "wa"))
        self.assertTrue(HS.small_towns("gfs", "wa"))

    def test_hrrr_and_nbm_cover_the_whole_frame(self):
        """No blank wedges: every panel sample sits on the CONUS grids."""
        from test_pnwwide_crop import hrrr_ij, nbm_ij, samples
        import numpy as np
        HRRR_NY, HRRR_NX = 1059, 1799
        NBM_NY, NBM_NX = 1597, 2345
        cam = CAM.Camera(view_of("wa"))
        try:
            pts = samples(cam, nx=36, ny=22)
            to_h, to_n = hrrr_ij(), nbm_ij()
            for lon, lat in pts:
                fi, fj = to_h(lon, lat)
                self.assertTrue(0 <= fi <= HRRR_NY - 1 and 0 <= fj <= HRRR_NX - 1, (lon, lat, fi, fj))
                fi, fj = to_n(lon, lat)
                self.assertTrue(0 <= fi <= NBM_NY - 1 and 0 <= fj <= NBM_NX - 1, (lon, lat, fi, fj))
        finally:
            cam.close()


if __name__ == "__main__":
    unittest.main()
