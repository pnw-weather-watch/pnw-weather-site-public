"""Tight and wide Pacific Northwest frames.

The tight view has to show all of Washington past 49N and all of Oregon to 42N,
widened in longitude so the 16:9 slot is not stretched, and every corner has to
stay on the HRRR grid. The wide view is the zoomed-out companion. It fits the
national blend. HRRR does not cover it.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import cartopy.crs as ccrs
import matplotlib
matplotlib.use("Agg")
import numpy as np

import camera as CAM
from test_static_models import REGIONS, view_dict

HRRR_NY, HRRR_NX = 1059, 1799
NBM_NY, NBM_NX = 1597, 2345


def hrrr_ij():
    rad = 6371229.0
    globe = ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad)
    hp = ccrs.LambertConformal(globe=globe, central_longitude=-97.5, central_latitude=38.5, standard_parallels=(38.5, 38.5))
    pc = ccrs.PlateCarree()
    sw = hp.transform_point(-122.719528, 21.138123, pc)

    def to_ij(lon, lat):
        x, y = hp.transform_point(float(lon), float(lat), pc)
        return (float(y) - float(sw[1])) / 3000.0, (float(x) - float(sw[0])) / 3000.0

    return to_ij


def nbm_ij():
    rad = 6371200.0
    globe = ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad)
    hp = ccrs.LambertConformal(globe=globe, central_longitude=-95.0, central_latitude=25.0, standard_parallels=(25.0, 25.0))
    pc = ccrs.PlateCarree()
    sw = hp.transform_point(-126.2766, 19.229, pc)

    def to_ij(lon, lat):
        x, y = hp.transform_point(float(lon), float(lat), pc)
        return (float(y) - float(sw[1])) / 2539.703, (float(x) - float(sw[0])) / 2539.703

    return to_ij


def panel_samples(cam, nx=21, ny=13):
    W, H = cam.size()
    x0, y0, w, h = cam.panel()
    out = []
    for fy in np.linspace(0, 1, ny):
        for fx in np.linspace(0, 1, nx):
            lon, lat = cam.lonlat(x0 + fx * w, y0 + fy * h)
            if lon > 180:
                lon -= 360
            out.append((lon, lat))
    return out


def frac(cam, lon, lat):
    x, y = cam.pixel(lon, lat)
    x0, y0, w, h = cam.panel()
    return (x - x0) / w, (y - y0) / h


class PnwWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tight = CAM.Camera(view_dict("pnwhr"))
        cls.wide = CAM.Camera(view_dict("pnwwide"))

    @classmethod
    def tearDownClass(cls):
        cls.tight.close()
        cls.wide.close()

    def test_slot_keeps_true_shape(self):
        for cam in (self.tight, self.wide):
            x0, x1, y0, y1 = cam.bounds()
            slot = cam.layout["axes"]
            W, H = cam.fig.get_size_inches()
            aspect = (slot[2] * W) / (slot[3] * H)
            self.assertAlmostEqual((x1 - x0) / (y1 - y0), aspect, places=3)

    def test_tight_covers_washington_and_oregon_inside_hrrr(self):
        places = {
            "vancouver": (49.2827, -123.1207),
            "victoria": (48.4284, -123.3656),
            "blaine": (49.00, -122.75),
            "neah": (48.37, -124.72),
            "spokane": (47.66, -117.43),
            "seattle": (47.61, -122.33),
            "portland": (45.52, -122.68),
            "brookings": (42.05, -124.28),
            "ontario": (44.03, -116.96),
            "medford": (42.33, -122.87),
        }
        for lon in np.linspace(-124.5, -117.05, 8):
            places[f"or-{lon:.1f}"] = (42.02, float(lon))
            places[f"wa-{lon:.1f}"] = (49.00, float(lon))
        for name, (lat, lon) in places.items():
            fx, fy = frac(self.tight, lon, lat)
            self.assertGreater(fx, 0.02, name)
            self.assertLess(fx, 0.98, name)
            self.assertGreater(fy, 0.015, name)
            self.assertLess(fy, 0.985, name)
        to_ij = hrrr_ij()
        for lon, lat in panel_samples(self.tight, 25, 15):
            fi, fj = to_ij(lon, lat)
            self.assertGreaterEqual(fi, -0.5, (lon, lat, fi))
            self.assertLessEqual(fi, HRRR_NY - 0.5, (lon, lat, fi))
            self.assertGreaterEqual(fj, -0.5)
            self.assertLessEqual(fj, HRRR_NX - 0.5)

    def test_wide_covers_the_inland_northwest_inside_nbm(self):
        places = {
            "reno": (39.53, -119.81),
            "redding": (40.59, -122.39),
            "elko": (40.83, -115.76),
            "calgary": (51.05, -114.07),
            "vancouver": (49.28, -123.12),
            "lethbridge": (49.69, -112.83),
            "helena": (46.59, -112.04),
            "bozeman": (45.68, -111.04),
            "boise": (43.62, -116.21),
            "brookings": (42.05, -124.28),
            "flattery": (48.38, -124.73),
        }
        for name, (lat, lon) in places.items():
            fx, fy = frac(self.wide, lon, lat)
            self.assertGreater(fx, 0.02, name)
            self.assertLess(fx, 0.98, name)
            self.assertGreater(fy, 0.015, name)
            self.assertLess(fy, 0.985, name)
        to_ij = nbm_ij()
        outside = 0
        for lon, lat in panel_samples(self.wide, 25, 15):
            fi, fj = to_ij(lon, lat)
            if not (0 <= fi <= NBM_NY - 1 and 0 <= fj <= NBM_NX - 1):
                outside += 1
        self.assertEqual(outside, 0)
        # The same rectangle leaves the HRRR domain, so that model does not list it.
        self.assertNotIn("pnwwide", REGIONS["model_views"]["hrrr"])
        self.assertIn("pnwwide", REGIONS["model_views"]["nbm"])
        self.assertIn("pnwwide", REGIONS["model_views"]["gfs"])


if __name__ == "__main__":
    unittest.main()
