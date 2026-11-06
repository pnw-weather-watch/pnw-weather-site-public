"""Hawaii wide view: closer north-south, same longitude span, every main island inside."""
import json
import os
import unittest

REGIONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))
# Main-island extremes that must stay inside the frame with a margin.
ISLANDS = {
    "Niihau": (21.90, -160.25),
    "Kauai": (22.23, -159.50),
    "Oahu": (21.71, -158.28),
    "Molokai": (21.22, -157.32),
    "Lanai": (20.83, -156.95),
    "Maui": (20.58, -156.00),
    "Big Island south": (18.91, -155.68),
    "Big Island east": (19.55, -154.82),
}


class HiwView(unittest.TestCase):
    def setUp(self):
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["hiw"]

    def test_closer_and_wider_than_a_plain_zoom(self):
        w, e, s, n = self.v["ll"]
        self.assertEqual([w, e, s, n], [-168.0, -148.0, 16.08, 24.42])
        self.assertAlmostEqual(e - w, 20.0, places=5)
        self.assertAlmostEqual(n - s, 8.34, places=2)
        self.assertAlmostEqual((w + e) / 2, -158.0, places=5)
        self.assertAlmostEqual((s + n) / 2, 20.25, places=2)
        self.assertEqual(self.v["proj"], ["merc", -158])
        self.assertEqual(self.v["size"], [16, 7])
        self.assertEqual(self.v["label"], "Hawaii (wide)")

    def test_main_islands_stay_inside_with_a_margin(self):
        w, e, s, n = self.v["ll"]
        for name, (lat, lon) in ISLANDS.items():
            self.assertGreater(lon, w + 0.4, name)
            self.assertLess(lon, e - 0.4, name)
            self.assertGreater(lat, s + 0.4, name)
            self.assertLess(lat, n - 0.4, name)
        bw, be, bs, bn = self.v["box"]
        self.assertLess(bw, w)
        self.assertGreater(be, e)
        self.assertLess(bs, s)
        self.assertGreater(bn, n)

    def test_frame_tuning(self):
        self.assertEqual(self.R["smooth"]["hiw"], 0.45)
        self.assertEqual(self.R["barbs_across"]["hiw"], 20)
        self.assertEqual(self.R["hl"]["radius_km"]["hiw"], 350)
        self.assertEqual(self.R["hl"]["prominence_mb"]["hiw"], 1.5)
        self.assertEqual(self.R["hl"]["edge_km"]["hiw"], 280)
        self.assertEqual(self.R["region_towns"]["hiw"], [[80000, 15000, 4000], 36])

    def test_models_that_had_hawaii_still_list_it(self):
        for m in ("gfs", "ifs", "ifs9", "aifs", "eps", "aens", "oisst", "gfsw", "epsm"):
            self.assertIn("hiw", self.R["model_views"][m], m)
        for m in ("hrrr", "rrfs", "nbm"):
            self.assertNotIn("hiw", self.R["model_views"][m], m)


if __name__ == "__main__":
    unittest.main()
