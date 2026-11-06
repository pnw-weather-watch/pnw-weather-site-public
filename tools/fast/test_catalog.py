"""The weather-bot list is already in this site, apart from Social HD loops and Compare TV mode.

Washington forecast views, WA Maps and the Studio are intentionally not added.
"""
import os
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENC = os.path.join(ROOT, "tools", "fast", "fast_encode.py")
VIEWER = os.path.join(ROOT, "tools", "fast", "site", "viewer.js")
INDEX = os.path.join(ROOT, "tools", "fast", "site", "index.html")
METEO = os.path.join(ROOT, "tools", "fast", "site", "meteograms.js")
OBS = os.path.join(ROOT, "web", "forecast", "obs", "obsimg.js")
WAVES = os.path.join(ROOT, "tools", "fast", "wave_views.py")
REGIONS = os.path.join(ROOT, "regions", "regions.json")


class Catalog(unittest.TestCase):
    def setUp(self):
        self.enc = open(ENC, encoding="utf-8").read()
        self.viewer = open(VIEWER, encoding="utf-8").read()

    def test_ifs9_stays_listed_while_publishing_is_paused(self):
        self.assertIn('"ifs9"', self.enc)
        self.assertIn('FAST_PAUSED', open(os.path.join(ROOT, ".github", "workflows", "fast-models.yml"), encoding="utf-8").read())
        self.assertIn("LISTED_WITHOUT_RUNS", self.viewer)
        self.assertIn('"ifs9"', self.viewer)

    def test_member_picker_covers_pressure_height_gust_and_snow(self):
        eps = open(os.path.join(ROOT, "tools", "fast", "eps_members.py"), encoding="utf-8").read()
        aens = open(os.path.join(ROOT, "tools", "fast", "aens_members.py"), encoding="utf-8").read()
        for name in ("mslp", "z500", "gust", "asnow"):
            self.assertIn(f'"{name}"', eps)
        for name in ("mslp", "z500", "asnow"):
            self.assertIn(f'"{name}"', aens)
        self.assertIn("AIFS ENS has no gust", aens)
        self.assertIn('max="50"', open(INDEX, encoding="utf-8").read())

    def test_severe_wave_ensemble_and_nbm_products_exist(self):
        for pid in ("refuh", "uh", "uhs", "cape3", "srh03", "lr03", "lr75",
                    "fog", "gustmax", "snow1", "ltng6", "ltgp",
                    "mslpqpf", "mslpa", "thick", "ptype", "aifswind",
                    "wavemax", "wavemax24", "swellhs",
                    "ehigh", "elow", "esnow", "eqpf90", "qpfa", "qpfpct",
                    "t2ma", "t850a", "z500anom", "et2sd", "epcape"):
            self.assertIn(f'"{pid}"', self.enc, pid)
        self.assertIn('prods = {k: prods[k] for k in ("t2m", "gust10", "tcc")}', self.enc)

    def test_pages_and_obs_are_wired(self):
        html = open(INDEX, encoding="utf-8").read()
        self.assertIn('id="play"', html)
        self.assertIn('id="save"', html)
        self.assertIn("Surface", self.viewer)
        self.assertIn("refreshPartial, 60e3", self.viewer)
        self.assertIn("SCALE_FLOOR_SNOWRATE = 3", open(METEO, encoding="utf-8").read())
        self.assertIn("SCALE_FLOOR_SNOW6 = 12", open(METEO, encoding="utf-8").read())
        obs = open(OBS, encoding="utf-8").read()
        self.assertIn("MRMS", obs)
        self.assertIn("GOES-West_ABI_Band13_Clean_Infrared", obs)
        self.assertIn("GOES-West_ABI_GeoColor", obs)
        self.assertIn("compare.html", html)

    def test_north_america_and_wave_only_west_coast(self):
        import json
        views = json.load(open(REGIONS, encoding="utf-8"))["views"]
        self.assertEqual(views["na"]["label"], "North America")
        waves = open(WAVES, encoding="utf-8").read()
        self.assertIn('"gfsw"', waves)
        self.assertIn("waveOnly=True", waves)
        self.assertIn("(-152.0, -116.0, 31.8, 49.8)", waves)

    def test_social_loops_and_tv_mode_are_not_added(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "tools", "fast", "site", "social.html")))
        self.assertNotIn("Exit TV", open(os.path.join(ROOT, "tools", "fast", "site", "compare.html"), encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
