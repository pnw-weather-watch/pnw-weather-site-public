"""Land is white on every product, including snow. Shoreline is GSHHG full."""
import json
import os
import re
import subprocess
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import house_style as HS

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
THEME = os.path.join(ROOT, "theme", "theme.json")
PIDS = ("t2m", "waves", "wavemax", "wavemax24", "swellhs", "frz", "snowlvl", "refc", "gust10", "qpf",
        "snow", "snow1", "snow6", "snow24", "kuchera", "dsnod", "esnow", "esnow90", "nsnow6", "nsnowtot")


class LandBase(unittest.TestCase):
    def test_every_product_is_white(self):
        with open(THEME, encoding="utf-8") as f:
            theme = json.load(f)
        self.assertEqual(theme["land_base"], "white")
        for pid, mode in theme.get("land_base_by_product", {}).items():
            self.assertEqual(mode, "white", pid)
        for pid in PIDS:
            self.assertEqual(HS.land_base(pid), "white", pid)
            self.assertEqual(HS.land_hex(pid), "#ffffff", pid)

    def test_shoreline_is_gshhg_full(self):
        with open(os.path.join(ROOT, "tools", "forecast", "house_style.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('GSHHSFeature(scale="full"', src)
        self.assertIn("def land(", src)
        with open(os.path.join(ROOT, "tools", "fast", "fast_encode.py"), encoding="utf-8") as f:
            enc = f.read()
        self.assertIn("CAM.sample_grid", enc)
        self.assertIn("HS.land(ax, cf)", enc)
        self.assertIn('prods[k]["min_show"] = 0.0', enc)

    def test_viewer_land_is_white_and_credit_clears_the_stamp(self):
        with open(os.path.join(ROOT, "tools", "fast", "site", "viewer.js"), encoding="utf-8") as f:
            src = f.read()
        land = re.search(r"function landHex\(pid, P\) \{.*?\n\}", src, re.S).group(0)
        width = re.search(r"function creditMaxWidth\(W, stampW\) \{.*?\n\}", src, re.S).group(0)
        script = land + "\n" + width + """
const bad = [];
for (const pid of ["t2m", "waves", "wavemax", "snow", "kuchera", "dsnod", "esnow", "nsnowtot"]) {
  if (landHex(pid, {}) !== "#ffffff") bad.push(pid);
  if (landHex(pid, {land_base: "black"}) !== "#ffffff") bad.push(pid + " override");
}
const W = 1920, stampW = 320, maxW = creditMaxWidth(W, stampW);
const right = W * 0.024 + maxW, stampLeft = W / 2 - stampW / 2;
if (right > stampLeft - 8) bad.push("credit overlaps stamp " + right + " vs " + stampLeft);
if (bad.length) { console.error(bad.join("\\n")); process.exit(1); }
"""
        subprocess.run(["node", "-e", script], check=True)


if __name__ == "__main__":
    unittest.main()
