"""The wide Pacific Northwest frame has to sit inside each model's stored crop.

NBM's previously published crop stopped at column 847. Denver is column ~940 and the
east edge of pnwwide is column ~1270, both on the CONUS grid. That is the white wedge.
Global 0.25 deg crops that already include North America already cover this frame.
"""
import contextlib
import datetime as dt
import io
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
        cls.tight = CAM.Camera(view_dict("pnwhr", hires=True))

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

    def test_hrrr_wide_frame_extends_past_the_conus_edge_and_the_crop_covers_it(self):
        fi, fj = self._grid(self.wide, hrrr_ij())
        native = (fi >= 0) & (fi <= 1058) & (fj >= 0) & (fj <= 1798)
        self.assertGreater(float((~native).mean()), 0.04)
        self.assertLess(float((~native).mean()), 0.15)
        # The cities sit on the native grid. The pad is ocean and the northern strip.
        for lat, lon in ((49.28, -123.12), (51.05, -114.07), (47.61, -122.33)):
            a, b = hrrr_ij()(lon, lat)
            self.assertTrue(0 <= a <= 1058 and 0 <= b <= 1798, (lat, lon, a, b))
        crop = FE.crop_bounds(fi, fj, 1059, 1799, outside=FE.CONUS_OUTSIDE)
        self.assertLess(crop[2], 0)
        self.assertGreater(crop[1], 1059)
        self.assertLessEqual(crop[0], fi.min())
        self.assertGreaterEqual(crop[1], fi.max())
        self.assertLessEqual(crop[2], fj.min())
        self.assertGreaterEqual(crop[3], fj.max())
        # Every wide-frame sample lands inside the extended array.
        rel_i, rel_j = fi - crop[0], fj - crop[2]
        self.assertTrue(np.all((rel_i >= 0) & (rel_i < crop[1] - crop[0])))
        self.assertTrue(np.all((rel_j >= 0) & (rel_j < crop[3] - crop[2])))
        # The California view is already off the domain to the west. A pad that stops at 90 cells
        # would fill part of that ocean and then go white. The pad has to cover it.
        ca = CAM.Camera(view_dict("ca"))
        cfi, cfj = self._grid(ca, hrrr_ij())
        ca.close()
        short = FE.crop_bounds(np.concatenate([fi, cfi]), np.concatenate([fj, cfj]), 1059, 1799, outside=90)
        full = FE.crop_bounds(np.concatenate([fi, cfi]), np.concatenate([fj, cfj]), 1059, 1799, outside=FE.CONUS_OUTSIDE)
        self.assertFalse(np.all((cfi >= short[0]) & (cfi < short[1]) & (cfj >= short[2]) & (cfj < short[3])))
        self.assertTrue(np.all((cfi >= full[0]) & (cfi < full[1]) & (cfj >= full[2]) & (cfj < full[3])))

    def test_nine_km_grid_covers_the_wide_frame_with_no_pad(self):
        pts = samples(self.wide)
        fi, fj = [], []
        for lon, lat in pts:
            fi.append((90.0 - lat) / 0.1)
            fj.append(((lon % 360) + 360) % 360 / 0.1)
        fi, fj = np.array(fi), np.array(fj)
        self.assertTrue(np.all((fi >= 0) & (fi <= 1800) & (fj >= 0) & (fj <= 3599)))
        crop = FE.crop_bounds(fi, fj, 1801, 3600)
        self.assertGreaterEqual(crop[0], 0)
        self.assertLessEqual(crop[2], fj.min())
        self.assertGreaterEqual(crop[3], fj.max())
        self.assertGreater(crop[3], 2500)

    def test_edge_blend_matches_across_the_domain_boundary(self):
        w = FE.conus_edge_weight(-4, 20, -4, 16, 10, 10, band=4)
        # Native column j=0 is index 4. The cell just outside, j=-1, is index 3. Both are pure donor.
        self.assertAlmostEqual(float(w[8, 4]), 1.0)
        self.assertAlmostEqual(float(w[8, 3]), 1.0)
        # 4 cells inside the west edge the weight is back to the native field.
        self.assertAlmostEqual(float(w[8, 8]), 0.0)
        jump = np.max(np.abs(np.diff(w, axis=1)))
        self.assertLessEqual(float(jump), 0.25 + 1e-6)
        native = np.full(w.shape, 10.0)
        native[:, :4] = np.nan
        donor = np.zeros(w.shape)
        out = FE.paint_edge(native, donor, w)
        # Outside the west edge and on the edge cell the value is the donor. Deep inside it is untouched.
        self.assertAlmostEqual(float(out[8, 3]), 0.0)
        self.assertAlmostEqual(float(out[8, 4]), 0.0)
        self.assertAlmostEqual(float(out[8, 8]), 10.0)
        # A categorical field must not average the two codes.
        codes = FE.paint_edge(np.full(w.shape, 16.0), np.full(w.shape, 32.0), w, categorical=True)
        self.assertTrue(set(np.unique(codes)).issubset({16.0, 32.0}))

    def test_take_crop_pads_with_nan_instead_of_wrapping(self):
        a = np.arange(20, dtype=float).reshape(4, 5)
        out = FE.take_crop(a, 1, 3, -2, 2)
        self.assertEqual(out.shape, (2, 4))
        self.assertTrue(np.all(np.isnan(out[:, :2])))
        self.assertTrue(np.allclose(out[:, 2:], a[1:3, 0:2]))

    def test_gfs_donor_hour_and_sample_and_grid_origin(self):
        self.assertEqual(FE.gfs_donor_hour(1), 0)
        self.assertEqual(FE.gfs_donor_hour(2), 3)
        self.assertEqual(FE.gfs_donor_hour(3), 3)
        self.assertEqual(FE.gfs_donor_hour(5), 6)
        c = dt.datetime(2026, 11, 8, 6, tzinfo=dt.timezone.utc)
        slots = [(f"{dc:%Y%m%d%H}", h) for dc, h in FE.gfs_donor_slots(c, 1)]
        self.assertEqual(slots, [("2026110806", 0), ("2026110800", 6), ("2026110718", 12), ("2026110712", 18)])
        self.assertNotIn("asnow", FE.GFS_EDGE_FIELDS)
        self.assertIn("asnow", FE.QUIET_EDGE_FIELDS)
        self.assertIn("t2m", FE.GFS_EDGE_FIELDS)
        ny, nx = 721, 1440
        lat_res = 180.0 / (ny - 1)
        field = (90.0 - np.arange(ny) * lat_res)[:, None] * np.ones((1, nx))
        got = FE.sample_ll(field, np.array([[45.0, 10.0]]), np.array([[-120.0, 0.0]]))
        self.assertAlmostEqual(float(got[0, 0]), 45.0, places=4)
        self.assertAlmostEqual(float(got[0, 1]), 10.0, places=4)
        self.assertFalse(FE.same_grid({"grid": {"ny": 1100, "nx": 800, "i0": 0, "j0": 0}}, [-20, 1080, -40, 760]))
        self.assertTrue(FE.same_grid({"grid": {"ny": 1100, "nx": 800, "i0": -20, "j0": -40}}, [-20, 1080, -40, 760]))

    def test_gfs_donor_uses_the_previous_cycle_when_this_one_is_not_posted(self):
        # HRRR 06Z f001/f002 ask for GFS 06Z f000/f003. Those indexes are not up yet; 00Z f006/f009 are.
        c = dt.datetime(2026, 11, 8, 6, tzinfo=dt.timezone.utc)
        posted = {("2026110800", 6), ("2026110800", 9)}
        asked = []

        def ready(cycle, hour):
            key = (f"{cycle:%Y%m%d%H}", hour)
            asked.append(key)
            return key in posted

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            f001 = FE.gfs_donor_for(c, 1, ready)
            f002 = FE.gfs_donor_for(c, 2, ready)
        self.assertEqual((f"{f001[0]:%Y%m%d%H}", f001[1]), ("2026110800", 6))
        self.assertEqual((f"{f002[0]:%Y%m%d%H}", f002[1]), ("2026110800", 9))
        self.assertEqual(asked[:2], [("2026110806", 0), ("2026110800", 6)])
        text = buf.getvalue()
        self.assertIn("edge donor 2026110806 f001: real 2026110800 f006", text)
        self.assertIn("edge donor 2026110806 f002: real 2026110800 f009", text)
        native = np.full((5, 5), 10.0)
        cropped = FE.take_crop(native, 0, 5, -1, 5)
        seen = []

        def get(R, model):
            seen.append((f"{R.c:%Y%m%d%H}", R.s, model))
            return np.full((721, 1440), 3.0)

        out = FE.fill_conus_outside("t2m", cropped, (0, 5, -1, 5), native.shape, c, 1, get, ready=ready)
        self.assertEqual(seen, [("2026110800", 6, "gfs")])
        self.assertAlmostEqual(float(out[2, 0]), 3.0)

    def test_gfs_donor_holds_when_none_of_the_cycles_are_posted(self):
        c = dt.datetime(2026, 11, 8, 6, tzinfo=dt.timezone.utc)
        asked = []

        def ready(cycle, hour):
            asked.append((f"{cycle:%Y%m%d%H}", hour))
            return False

        native = np.arange(25, dtype=float).reshape(5, 5)
        cropped = FE.take_crop(native, 0, 5, -1, 5)
        called = []

        def get(R, model):
            called.append(R)
            raise AssertionError("donor fetch")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = FE.fill_conus_outside("t2m", cropped, (0, 5, -1, 5), native.shape, c, 2, get, ready=ready)
        self.assertEqual(called, [])
        self.assertEqual(asked, [("2026110806", 3), ("2026110800", 9), ("2026110718", 15), ("2026110712", 21)])
        self.assertIn("edge donor 2026110806 f002: held", buf.getvalue())
        # The column past the west edge keeps the boundary cell, not a fetched field.
        self.assertTrue(np.allclose(out[:, 0], cropped[:, 1]))

    def test_stale_cycles_follow_the_newest(self):
        import fast_cycle as FC
        newest = 2
        self.assertEqual(FC.cycles_to_encode(newest, [2, 1, 0]), [2, 1, 0])
        self.assertEqual(FC.cycles_to_encode(None, [1]), [1])
        self.assertEqual(FC.cycles_to_encode(3, []), [3])

    def test_longitude_box_matches_either_sign_convention(self):
        lo = np.array([230.0, 255.0, 300.0])  # 0..360, same NBM longitudes
        self.assertTrue(bool(FE._lon_in(lo, -136, -95)[1]))
        self.assertFalse(bool(FE._lon_in(lo, -136, -95)[2]))


if __name__ == "__main__":
    unittest.main()
