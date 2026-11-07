"""Town names grow by population tier. Buoy type is not part of this."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import house_style as HS


class TownTiers(unittest.TestCase):
    def test_major_cities_are_largest_and_small_towns_grew(self):
        self.assertGreater(HS.TOWN_PT[1], HS.TOWN_PT[2])
        self.assertGreater(HS.TOWN_PT[2], HS.TOWN_PT[3])
        self.assertGreater(HS.TOWN_PT[3], 8.0)   # small towns were 8 pt
        for name in ("Seattle", "Portland", "Honolulu", "Los Angeles", "San Francisco", "Sacramento"):
            self.assertEqual(HS.town_tier(name), 1, name)
            self.assertEqual(HS.town_tier(name, 3), 1, name)
        self.assertEqual(HS.town_tier("Spokane"), 2)
        self.assertEqual(HS.town_tier("Forks"), 3)
        self.assertEqual(HS.town_tier("Forks", 2), 2)
        self.assertGreater(HS.TOWN_HALO_W[1], HS.TOWN_HALO_W[3])


if __name__ == "__main__":
    unittest.main()
