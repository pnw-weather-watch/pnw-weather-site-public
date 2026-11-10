"""Products derived from fields the open files actually publish."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_encode as fe


class DerivedFields(unittest.TestCase):
    def test_freezing_level_crosses_between_1000_and_925(self):
        # 10 C at 100 m, -5 C at 800 m. The 0 C surface is one third of the way up from 1000 hPa.
        shape = (2, 2)
        T, Z = [], []
        for k, lev in enumerate(fe.FRZ_LEVELS_HPA):
            if lev == 1000:
                T.append(np.full(shape, 283.15)); Z.append(np.full(shape, 100.0))
            elif lev == 925:
                T.append(np.full(shape, 268.15)); Z.append(np.full(shape, 800.0))
            else:
                T.append(np.full(shape, 250.0)); Z.append(np.full(shape, 2000.0 + k))
        z = fe.freezing_level_m(T, Z)
        self.assertTrue(np.allclose(z, 100 + (10 / 15) * 700))

    def test_freezing_level_already_below_freezing_uses_the_ground_level(self):
        shape = (1, 1)
        T = [np.full(shape, 260.0) for _ in fe.FRZ_LEVELS_HPA]
        Z = [np.full(shape, 400.0 + 100 * k) for k in range(len(fe.FRZ_LEVELS_HPA))]
        z = fe.freezing_level_m(T, Z)
        self.assertTrue(np.allclose(z, 400.0))

    def test_underground_levels_are_skipped(self):
        # Surface pressure is 900 hPa, so 1000 hPa is below ground. Crossing is 925 (5 C) to 850 (-5 C).
        shape = (1, 1)
        T, Z = [], []
        for lev in fe.FRZ_LEVELS_HPA:
            if lev == 1000:
                T.append(np.full(shape, 290.0)); Z.append(np.full(shape, -100.0))
            elif lev == 925:
                T.append(np.full(shape, 278.15)); Z.append(np.full(shape, 1000.0))
            elif lev == 850:
                T.append(np.full(shape, 268.15)); Z.append(np.full(shape, 1600.0))
            else:
                T.append(np.full(shape, 250.0)); Z.append(np.full(shape, 3000.0))
        z = fe.freezing_level_m(T, Z, sp_pa=np.full(shape, 98000.0))
        self.assertTrue(np.allclose(z, 1300.0))

    def test_gfs_snowfall_is_ten_to_one_and_ignores_the_snow_depth_sentinel(self):
        import numpy as np
        swe = np.array([0.0, 25.4, 25.4, 9999.0])  # kg/m2: 0, 1 inch, 1 inch, nonsense
        frac = np.array([1.0, 0.0, 0.5, 1.0])
        out = fe.gfs_snowfall_in(swe, frac)
        self.assertAlmostEqual(float(out[0]), 0.0)
        self.assertAlmostEqual(float(out[1]), 0.0)
        self.assertAlmostEqual(float(out[2]), 5.0, places=4)
        self.assertEqual(float(out[3]), 0.0)
        pct = fe.gfs_snowfall_in(np.array([25.4]), np.array([50.0]))
        self.assertAlmostEqual(float(pct[0]), 5.0, places=4)

    def test_gfs_snow_bucket_is_the_short_window_after_f6(self):
        # Lines copied from the 2026-11-07 12Z pgrb2 idx. The instantaneous flag is not the average.
        f003 = ["1:0:d=2026110712:CSNOW:surface:3 hour fcst:", "2:1:d=2026110712:CSNOW:surface:0-3 hour ave fcst:"]
        f012 = ["1:0:d=2026110712:CSNOW:surface:12 hour fcst:", "2:1:d=2026110712:CSNOW:surface:6-12 hour ave fcst:"]
        f120 = ["9:0:d=2026110712:CSNOW:surface:114-120 hour ave fcst:"]
        self.assertEqual(fe.gfs_snow_bucket(f003), (0, 3))
        self.assertEqual(fe.gfs_snow_bucket(f012), (6, 12))
        self.assertEqual(fe.gfs_snow_bucket(f120), (114, 120))
        with self.assertRaises(KeyError):
            fe.gfs_snow_bucket(["1:0:d=2026110712:CSNOW:surface:12 hour fcst:"])

    def test_gfs_six_hour_bucket_does_not_drop_the_total(self):
        # F9 is 1 inch of liquid, all snow: 10 inches. F12's 6-hour mean is only half snow,
        # and the extra 3 hours are dry, so stacking apcp(6-12) x f(6-12) would fall to 5.
        # The trailing 3 hours are dry, so the total stays 10.
        steps = [
            (3, 0, 3, 0.0, 0.0),
            (6, 0, 6, 0.0, 0.0),
            (9, 6, 9, 25.4, 1.0),
            (12, 6, 12, 25.4, 0.5),
        ]
        totals = fe.gfs_snow_running(steps)
        self.assertAlmostEqual(float(totals[9]), 10.0, places=4)
        self.assertAlmostEqual(float(totals[12]), 10.0, places=4)
        self.assertGreaterEqual(float(totals[12]), float(totals[9]) - 1e-4)

    def test_gfs_full_run_snow_never_decreases_and_matches_ten_to_one(self):
        # Every 3 h from F+3 through F+384, the same layout as the 2026-11-07 12Z idx:
        # hour % 6 == 3 is a 3 h bucket; hour % 6 == 0 is the 6 h bucket with the same start.
        rng = np.random.default_rng(7)
        hours = list(range(3, 385, 3))
        true = {}
        steps = []
        water = np.zeros((2, 2))
        for h in hours:
            swe3 = rng.uniform(0, 6, (2, 2))
            frac3 = rng.uniform(0, 1, (2, 2))
            true[h] = fe.gfs_snowfall_in(swe3, frac3)
            water = water + np.asarray(swe3) * np.clip(frac3, 0, 1)
            if h % 6 == 3:
                steps.append((h, h - 3, h, swe3, frac3))
            else:
                swe_a, frac_a = steps[-1][3], steps[-1][4]
                steps.append((h, h - 6, h, swe_a + swe3, (3 * frac_a + 3 * frac3) / 6))
        totals = fe.gfs_snow_running(steps)
        expect = np.zeros((2, 2))
        prev = None
        for h in hours:
            expect = expect + true[h]
            got = np.asarray(totals[h], float)
            self.assertTrue(np.all(got + 1e-3 >= (0 if prev is None else prev)))
            self.assertTrue(np.allclose(got, expect, atol=1e-3))
            prev = got
        # No melt: WEASD change at 10:1 is the same sum of (snow fraction x liquid).
        weasd = np.clip(water / 25.4 * 10.0, 0, fe.GFS_SNOW_MAX_IN)
        self.assertTrue(np.allclose(totals[384], weasd, atol=1e-2))
        self.assertLess(float(np.max(totals[384])), 500.1)
        sentinel = fe.gfs_snowfall_in(np.full((2, 2), 9999.0), np.ones((2, 2)))
        self.assertTrue(np.all(sentinel == 0))
        self.assertLess(float(np.max(sentinel)) * len(hours), 393662)

    def test_gfs_cloud_top_uses_the_coldest_layer_and_2m_when_clear(self):
        high = np.array([[220.0, np.nan]])
        mid = np.array([[250.0, np.nan]])
        low = np.array([[270.0, np.nan]])
        t2 = np.array([[280.0, 290.0]])
        c = fe.gfs_cloud_top_c([high, mid, low], t2)
        # The coldest finite cloud top wins. A clear column (no finite top) uses 2 m temperature.
        self.assertAlmostEqual(float(c[0, 0]), 220.0 - 273.15, places=3)
        self.assertAlmostEqual(float(c[0, 1]), 290.0 - 273.15, places=3)

    def test_color_key_is_written_for_a_north_america_view(self):
        import os
        import tempfile
        spec = {"refc": {
            "key": "Reflectivity (dBZ)", "tickfmt": True,
            "levels": [5, 15, 25, 35], "ticks": [5, 15, 25],
            "colors": ["#04e9e7", "#019ff4", "#0300f4"],
            "under": None, "over": "#0300f4",
            "keys": {"na": "static/key_gfs_refc_na.png"},
        }}
        with tempfile.TemporaryDirectory() as d:
            paths = fe.write_product_keys("gfs", spec, d)
            self.assertIn("static/key_gfs_refc_na.png", paths)
            png = os.path.join(d, "static/key_gfs_refc_na.png")
            self.assertGreater(os.path.getsize(png), 1000)
            self.assertGreater(os.path.getsize(os.path.join(d, "static/x2/key_gfs_refc_na.png")), 1000)


    def test_freezing_level_850_and_700_below_freezing(self):
        # 11-08 (Weather Bot): 850 and 700 mb both below freezing, lower levels below ground (Alaska / interior BC).
        # Must NOT fall back to the top-of-profile height (that was the bogus ~30k ft).
        shape = (1, 1)
        T, Z = [], []
        z_of = {850: 1400.0, 700: 3000.0, 600: 4200.0, 500: 5500.0, 400: 7200.0, 300: 9000.0}
        for lev in fe.FRZ_LEVELS_HPA:
            if lev <= 850:
                T.append(np.full(shape, 255.0)); Z.append(np.full(shape, z_of[lev]))
            else:
                T.append(np.full(shape, 250.0)); Z.append(np.full(shape, -200.0))  # below ground
        z = fe.freezing_level_m(T, Z, sp_pa=np.full(shape, 85000.0))  # ~850 hPa surface
        self.assertTrue(np.allclose(z, 1400.0), msg=f"got {z}; must be the 850 mb height, not the top")


if __name__ == "__main__":
    unittest.main()
