"""The wide Pacific Northwest frame has to sit inside each model's stored crop.

NBM's previously published crop stopped at column 847. Denver is column ~940 and the
east edge of pnwwide is column ~1270, both on the CONUS grid. That is the white wedge.
Global 0.25 deg crops that already include North America already cover this frame.
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
import fast_encode as FE
from test_static_models import view_dict

# NBM CONUS grid, from the operational GRIB (Nx 2345, Ny 1597, first point 19.229N 233.7234E).
NBM_NY, NBM_NX = 1597, 2345
NBM_DX = 2539.703


def nbm_ij():
    globe = ccrs.Globe(ellipse="sphere", semimajor_axis=6371200.0, semiminor_axis=6371200.0)
    hp = ccrs.LambertConformal(globe=globe, central_longitude=-95.0, central_latitude=25.0, standard_parallels=(25.0, 25.0))
    pc = ccrs.PlateCarree()
    sw = hp.transform_point(-126.2766, 19.229, pc)

    def to_ij(lon, lat):
        x, y = hp.transform_point(float(lon), float(lat), pc)
        return (float(y) - float(sw[1])) / NBM_DX, (float(x) - float(sw[0])) / NBM_DX

    return to_ij


def hrrr_ij():
    globe = ccrs.Globe(ellipse="sphere", semimajor_axis=6371229.0, semiminor_axis=6371229.0)
    hp = ccrs.LambertConformal(globe=globe, central_longitude=-97.5, central_latitude=38.5, standard_parallels=(38.5, 38.5))
    pc = ccrs.PlateCarree()
    sw = hp.transform_point(-122.719528, 21.138123, pc)

    def to_ij(lon, lat):
        x, y = hp.transform_point(float(lon), float(lat), pc)
        return (float(y) - float(sw[1])) / 3000.0, (float(x) - float(sw[0])) / 3000.0

    return to_ij


def samples(cam, nx=28, ny=18):
    x0, y0, w, h = cam.panel()
    fi, fj = [], []
    for fy in np.linspace(0, 1, ny):
        for fx in np.linspace(0, 1, nx):
            lon, lat = cam.lonlat(x0 + fx * w, y0 + fy * h)
            if lon > 180:
                lon -= 360
            fi.append(lat)  # placeholder, replaced by caller
            fj.append((lon, lat))
    return fj


class WideCrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wide = CAM.Camera(view_dict("pnwwide"))
        cls.tight = CAM.Camera(view_dict("pnwhr"))

    @classmethod
    def tearDownClass(cls):
        cls.wide.close()
        cls.tight.close()

    def _grid(self, cam, to_ij):
        pts = samples(cam)
        fi, fj = [], []
        for lon, lat in pts:
            a, b = to_ij(lon, lat)
            fi.append(a)
            fj.append(b)
        return np.array(fi), np.array(fj)

    def test_nbm_crop_covers_the_wide_frame_past_the_old_east_edge(self):
        fi, fj = self._grid(self.wide, nbm_ij())
        self.assertTrue(np.all((fi >= 0) & (fi <= NBM_NY - 1) & (fj >= 0) & (fj <= NBM_NX - 1)))
        crop = FE.crop_bounds(fi, fj, NBM_NY, NBM_NX)
        den_fi, den_fj = nbm_ij()(-104.99, 39.74)
        # The crop that drew the wedge: columns stopped at 847, west of Denver.
        old = [336, 1486, 0, 847]
        self.assertFalse(old[2] <= den_fj < old[3])
        self.assertLess(crop[2], den_fj)
        self.assertGreater(crop[3], den_fj)
        self.assertLessEqual(crop[2], fj.min())
        self.assertGreaterEqual(crop[3], fj.max())
        self.assertGreater(crop[3], 1200)

    def test_global_quarter_degree_crop_already_covers_the_wide_frame(self):
        pts = samples(self.wide)
        fi, fj = [], []
        for lon, lat in pts:
            fi.append((90.0 - lat) / 0.25)
            fj.append(((lon % 360) + 360) % 360 / 0.25)
        fi, fj = np.array(fi), np.array(fj)
        # Historical GFS/IFS crop (North America included). Rows 8..361, cols 560..1421.
        old = [8, 361, 560, 1421]
        self.assertTrue(np.all((fi >= old[0]) & (fi < old[1]) & (fj >= old[2]) & (fj < old[3])))
        crop = FE.crop_bounds(fi, fj, 721, 1440)
        self.assertLessEqual(crop[2], fj.min())
        self.assertGreaterEqual(crop[3], fj.max())

    def test_hrrr_tight_frame_needs_columns_past_the_old_crop(self):
        fi, fj = self._grid(self.tight, hrrr_ij())
        crop = FE.crop_bounds(fi, fj, 1059, 1799)
        self.assertLessEqual(crop[2], fj.min())
        self.assertGreaterEqual(crop[3], fj.max())
        # Published HRRR crop ended at column 619. A filled tight frame needs further east.
        self.assertGreater(fj.max(), 619)
        self.assertGreater(crop[3], 619)

    def test_finished_run_on_the_old_grid_is_not_done(self):
        old = {"complete": True, "grid": {"ny": 1150, "nx": 847}}
        new_crop = [336, 1486, 0, 1280]
        self.assertFalse(FE.same_grid(old, new_crop))
        self.assertTrue(FE.same_grid({"grid": {"ny": 1150, "nx": 1280}}, new_crop))

    def test_longitude_box_matches_either_sign_convention(self):
        lo = np.array([230.0, 255.0, 300.0])  # 0..360, same NBM longitudes
        self.assertTrue(bool(FE._lon_in(lo, -136, -95)[1]))
        self.assertFalse(bool(FE._lon_in(lo, -136, -95)[2]))


if __name__ == "__main__":
    unittest.main()
