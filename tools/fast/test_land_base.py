"""Land is white, except every snow product, which is black. Shoreline is GSHHG full."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import house_style as HS

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
THEME = os.path.join(ROOT, "theme", "theme.json")
WHITE = ("t2m", "waves", "frz", "snowlvl", "refc", "gust10", "qpf")
BLACK = ("snow", "snow1", "snow6", "snow12", "snow24", "snow48",
         "kuchera", "kuch6", "kuch12", "kuch24", "kuch48", "dsnod",
         "esnow", "esnow6", "esnow12", "esnow24", "esnow48", "esnow90",
         "nsnow6", "nsnow12", "nsnow24", "nsnow48", "nsnowtot")


class LandBase(unittest.TestCase):
    def test_default_is_white_and_snow_is_black(self):
        with open(THEME, encoding="utf-8") as f:
            theme = json.load(f)
        self.assertEqual(theme["land_base"], "white")
        for pid in WHITE:
            self.assertEqual(HS.land_base(pid), "white", pid)
            self.assertEqual(HS.land_hex(pid), "#ffffff", pid)
        for pid in BLACK:
            self.assertEqual(theme["land_base_by_product"][pid], "black", pid)
            self.assertEqual(HS.land_base(pid), "black", pid)
            self.assertEqual(HS.land_hex(pid), "#000000", pid)
        self.assertEqual(HS.land_base(None), "white")

    def test_shoreline_is_gshhg_full_not_a_coarse_natural_earth(self):
        with open(os.path.join(ROOT, "tools", "forecast", "house_style.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('GSHHSFeature(scale="full"', src)
        self.assertNotIn('NaturalEarthFeature("physical", "coastline", "50m"', src)
        self.assertNotIn('NaturalEarthFeature("physical", "coastline", "110m"', src)
        with open(os.path.join(ROOT, "tools", "fast", "fast_encode.py"), encoding="utf-8") as f:
            enc = f.read()
        self.assertIn("HS.outlines(ax, cf, res=HS.COAST_RES)", enc)
        self.assertIn('P["land_base"] = HS.land_base(_pid)', enc)
        self.assertEqual(HS.COAST_RES, "full")

    def test_viewer_uses_the_same_product_rule(self):
        import re
        import subprocess
        with open(os.path.join(ROOT, "tools", "fast", "site", "viewer.js"), encoding="utf-8") as f:
            src = f.read()
        fn = re.search(r"function landHex\(pid, P\) \{.*?\n\}", src, re.S).group(0)
        black = json.dumps(list(BLACK))
        white = json.dumps(list(WHITE))
        script = fn + f"""
const bad = [];
for (const pid of {black}) if (landHex(pid, {{}}) !== "#000000") bad.push(pid + " not black");
for (const pid of {white}) if (landHex(pid, {{}}) !== "#ffffff") bad.push(pid + " not white");
if (landHex("snow", {{land_base: "white"}}) !== "#ffffff") bad.push("manifest override ignored");
if (landHex("t2m", {{land_base: "black"}}) !== "#000000") bad.push("manifest black ignored");
if (bad.length) {{ console.error(bad.join("\\n")); process.exit(1); }}
"""
        subprocess.run(["node", "-e", script], check=True)


if __name__ == "__main__":
    unittest.main()
