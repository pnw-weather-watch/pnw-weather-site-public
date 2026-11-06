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

    def test_gfs_cloud_top_uses_the_coldest_layer_and_2m_when_clear(self):
        high = np.array([[220.0, np.nan]])
        mid = np.array([[250.0, np.nan]])
        low = np.array([[270.0, np.nan]])
        t2 = np.array([[280.0, 290.0]])
        c = fe.gfs_cloud_top_c([high, mid, low], t2)
        self.assertAlmostEqual(float(c[0, 0]), 220.0 - 273.15, places=3)
        self.assertAlmostEqual(float(c[0, 1]), 290.0 - 273.15, places=3)


if __name__ == "__main__":
    unittest.main()
