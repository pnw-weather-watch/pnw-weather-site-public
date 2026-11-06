"""California Passes: renamed label, I-5 Black Butte Summit, north edge past Mount Shasta."""
import json
import os
import unittest

REGIONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))


class CapassesView(unittest.TestCase):
    def setUp(self):
        with open(REGIONS) as f:
            self.R = json.load(f)
        self.v = self.R["views"]["capasses"]
        self.passes = self.R["CA_PASSES"]

    def test_label_is_california_passes(self):
        self.assertEqual(self.v["label"], "California Passes")
        self.assertNotIn("Sierra", self.v["label"])

    def test_black_butte_summit_is_the_i5_gap(self):
        p = self.passes["Black Butte Summit"]
        self.assertEqual(p["label"], "Black Butte")
        self.assertEqual(p["route"], "I-5")
        self.assertEqual(p["elev_ft"], 3912)
        self.assertAlmostEqual(p["lat"], 41.3546, places=4)
        self.assertAlmostEqual(p["lon"], -122.3539, places=4)
        self.assertIn("1657848", p["src"])

    def test_frame_reaches_shasta_and_keeps_tejon(self):
        w, e, s, n = self.v["ll"]
        self.assertGreaterEqual(n, 41.6)
        self.assertLessEqual(n, 41.8)
        self.assertLessEqual(s, 34.5)
        tejon = self.passes["Tejon Pass"]
        donner = self.passes["Donner Pass"]
        bb = self.passes["Black Butte Summit"]
        for name, lat, lon in (
            ("Tejon", tejon["lat"], tejon["lon"]),
            ("Donner", donner["lat"], donner["lon"]),
            ("Black Butte", bb["lat"], bb["lon"]),
        ):
            self.assertTrue(s < lat < n and w < lon < e, name)
        towns = {t[0]: (t[1], t[2]) for t in self.R["CA_PASS_TOWNS"]}
        for name in ("Redding", "Mount Shasta"):
            lat, lon = towns[name]
            self.assertTrue(s + 0.15 < lat < n - 0.15 and w + 0.15 < lon < e - 0.15, name)

    def test_models_that_draw_california_passes_still_list_it(self):
        have = [m for m, vs in self.R["model_views"].items() if "capasses" in vs]
        self.assertEqual(have, ["hrrr", "rrfs", "nbm", "gfs", "ifs", "ifs9"])


if __name__ == "__main__":
    unittest.main()
