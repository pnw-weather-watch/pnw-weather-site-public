"""Oregon coast is a wide ocean frame, and every encoded model still lists it."""
import json
import os
import unittest

REGIONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))
# Coast near 124.1 W should sit about a quarter of the width in from the right edge.
COAST = -124.1


class OrcoView(unittest.TestCase):
    def setUp(self):
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["orco"]

    def test_window_is_four_times_wider_and_land_is_the_right_quarter(self):
        w, e, s, n = self.v["ll"]
        self.assertEqual([w, e, s, n], [-132.5, -121.3, 41.95, 46.35])
        width = e - w
        self.assertAlmostEqual(width, 11.2, places=5)
        self.assertAlmostEqual(n - s, 4.4, places=5)  # Astoria to Brookings, unchanged
        # fraction of the width to the right of the coast
        self.assertAlmostEqual((e - COAST) / width, 0.25, places=2)
        self.assertEqual(self.v["proj"][:3], ["lcc", -126.9, 44.15])
        self.assertEqual(self.v["size"], [16, 11.1])
        bw, be, bs, bn = self.v["box"]
        self.assertLess(bw, w)
        self.assertGreater(be, e)
        self.assertLess(bs, s)
        self.assertGreater(bn, n)

    def test_wider_frame_tuning(self):
        self.assertEqual(self.R["smooth"]["orco"], 0.4)
        self.assertEqual(self.R["barbs_across"]["orco"], 22)
        self.assertEqual(self.R["hl"]["radius_km"]["orco"], 300)
        self.assertEqual(self.R["hl"]["prominence_mb"]["orco"], 1.5)
        self.assertEqual(self.R["hl"]["edge_km"]["orco"], 300)
        self.assertEqual(self.R["region_towns"]["orco"], [[120000, 40000, 10000], 32])

    def test_every_model_that_lists_views_includes_orco(self):
        missing = [m for m, vs in self.R["model_views"].items() if "orco" not in vs]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
