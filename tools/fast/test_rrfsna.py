"""RRFS 13 km North America (rrfsna) stays on the wide Pacific/NA views."""
import json
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))

import fast_encode as FE
import house_style as HS
import menu_maps as M

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
REGIONS = json.load(open(os.path.join(ROOT, "regions", "regions.json")))


class RrfsnaRegistration(unittest.TestCase):
    def test_model_is_rotated_latlon_and_reuses_rrfs_products(self):
        md = FE.MODELS["rrfsna"]
        self.assertEqual(md["grid"], "rotll")
        self.assertEqual(FE.as_model("rrfsna"), "rrfs")
        self.assertEqual(md["cycles"], (0, 6, 12, 18))
        self.assertEqual(md["steps"], list(range(1, 85)))
        self.assertIn("rrfsna", FE.NOAA)
        self.assertEqual(M.MODELS["rrfsna"]["url"], M.TM.RRFSNA)
        self.assertTrue(M.MODELS["rrfsna"].get("rotated_ll"))
        self.assertNotIn("rrfsna", M.HIRES)

    def test_wide_views_only_no_washington(self):
        want = ("na", "pac", "pnw", "pnwt", "pnwwide")
        self.assertEqual(tuple(REGIONS["model_views"]["rrfsna"]), want)
        self.assertEqual(FE.MODELS["rrfsna"]["views"], want)
        for tight in ("wa", "passes", "pnwhr", "ca", "socal", "cenca", "norca", "bay", "orco", "capasses"):
            self.assertNotIn(tight, REGIONS["model_views"]["rrfsna"], tight)
            self.assertNotIn(tight, FE.MODELS["rrfsna"]["views"], tight)

    def test_credit_names_noaa_ncep_rrfs(self):
        self.assertEqual(M.credit("rrfsna"), "Data: NOAA/NCEP RRFS (public domain).  Basemap: Natural Earth.")
        self.assertIn("rrfsna", HS.GLOBAL_PNW_MODELS)
        self.assertNotIn("rrfsna", HS.HIRES_PNW_MODELS)

    def test_rotll_to_ij_matches_known_geographic_points(self):
        # Verified against the 1127x683 operational NA grid (00Z 2026-11-10).
        fi, fj = FE.rotll_to_ij(-122.3321, 47.6062)
        self.assertAlmostEqual(fi, 276.626, places=2)
        self.assertAlmostEqual(fj, 504.860, places=2)
        self.assertTrue(0 <= fi <= 682 and 0 <= fj <= 1126)
        fi, fj = FE.rotll_to_ij(-160.0, 40.0)
        self.assertTrue(0 <= fi <= 682 and 0 <= fj <= 1126)
        # Corners of the native grid, from eccodes latlons().
        fi, fj = FE.rotll_to_ij(-157.378928, -1.557179)
        self.assertAlmostEqual(fi, 0.0, places=3)
        self.assertAlmostEqual(fj, 0.0, places=3)

    def test_rrfs_products_stay_on_the_menu(self):
        for pid in ("refc", "snow", "frz", "vis", "ir", "gust10", "gust6"):
            self.assertTrue(FE.menu_keeps(pid, {}, "rrfsna"), pid)

    
    def test_incremental_fields_reread_the_same_na_grid(self):
        # Getters see as_model "rrfs"; previous-step SNOD / APCP must still open rrfsna, not CONUS RRFS.
        src = open(os.path.join(os.path.dirname(__file__), "fast_encode.py"), encoding="utf-8").read()
        self.assertIn('M.Reader(R.m, R.c, s0)', src)
        self.assertIn('M.Reader(R.m, R.c, 0)', src)
        self.assertNotIn('M.Reader(m, R.c, s0)', src)
        self.assertNotIn('M.Reader(m, R.c, 0)', src)

    
    def test_grib_bitmap_missing_values_are_masked(self):
        src = open(os.path.join(os.path.dirname(__file__), "..", "forecast", "menu_maps.py"), encoding="utf-8").read()
        self.assertIn("bitmapPresent", src)
        self.assertIn("missingValue", src)

    
    def test_acc0_accepts_day_labeled_run_totals(self):
        # F48/F72 (and F24) NA files label APCP/ASNOW run totals "0-N day acc fcst".
        src = open(os.path.join(os.path.dirname(__file__), "..", "forecast", "menu_maps.py"), encoding="utf-8").read()
        self.assertIn('"0-%d hour acc fcst" % self.s', src)
        self.assertIn('"0-%d day acc fcst" % (self.s // 24)', src)

    def test_winds_are_rotated_from_the_grid(self):
        src = open(os.path.join(os.path.dirname(__file__), "..", "forecast", "menu_maps.py"), encoding="utf-8").read()
        self.assertIn("rotll_earth_relative", src)
        self.assertIn("if M.get(\"rotated_ll\"): u, w = rotll_earth_relative", src)

    
    def test_missing_domain_cells_stay_transparent(self):
        src = open(os.path.join(os.path.dirname(__file__), "fast_encode.py"), encoding="utf-8").read()
        self.assertIn("def invalidate_missing_lut", src)
        self.assertIn("luts[vid] = invalidate_missing_lut(fi, fj, ang, GRID_VALID.get(m))", src)
        self.assertIn('if MODELS[m]["grid"] == "rotll":\n            # RRFS NA bitmap-missing cells', src)
        self.assertIn("a = fill_nearest_valid(a)", src)
        a = np.array([[np.nan, 1.0], [2.0, np.nan]])
        b = FE.fill_nearest_valid(a)
        self.assertTrue(np.isfinite(b).all())
        self.assertEqual(float(np.nanmin(b)), 1.0)

    def test_conus_edge_pad_does_not_apply(self):
        src = open(os.path.join(os.path.dirname(__file__), "fast_encode.py"), encoding="utf-8").read()
        self.assertIn('outside = CONUS_OUTSIDE if m in ("hrrr", "rrfs", "nbm") else 0', src)
        self.assertIn('if m in ("hrrr", "rrfs") and "pnwhr" in TM.VIEWS:', src)


if __name__ == "__main__":
    unittest.main()
