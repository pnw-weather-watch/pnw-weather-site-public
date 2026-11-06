"""Pass lists in the viewer match the encoder lists, including Black Butte."""
import json
import os
import re
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SEL = os.path.join(ROOT, "tools", "fast", "site", "selection.js")
PY = os.path.join(ROOT, "tools", "forecast", "temp_maps.py")
REGIONS = os.path.join(ROOT, "regions", "regions.json")
VIEWER = os.path.join(ROOT, "tools", "fast", "site", "viewer.js")


def js_passes(name, src):
    block = re.search(r"const %s = \[(.*?)\];" % name, src, re.S).group(1)
    out = []
    for m in re.finditer(
        r'id: "([^"]+)", label: "([^"]+)", lat: ([-\d.]+), lon: ([-\d.]+), elev: (\d+)',
        block,
    ):
        out.append((m.group(1), m.group(2), float(m.group(3)), float(m.group(4)), int(m.group(5))))
    return out


class PassLabels(unittest.TestCase):
    def test_cascade_passes_match_temp_maps(self):
        with open(SEL, encoding="utf-8") as f:
            src = f.read()
        with open(PY, encoding="utf-8") as f:
            py = f.read()
        body = py.split("WA_PASSES = {", 1)[1].split("}", 1)[0]
        py_rows = re.findall(
            r'"([^"]+)": \("([^"]+)", ([-\d.]+), ([-\d.]+), (\d+)\)',
            body,
        )
        js = js_passes("WA_PASSES", src)
        self.assertEqual(
            [(a, b, float(c), float(d), int(e)) for a, b, c, d, e in py_rows],
            js,
        )
        self.assertEqual(len(js), 9)

    def test_california_passes_match_regions(self):
        with open(REGIONS, encoding="utf-8") as f:
            R = json.load(f)
        with open(SEL, encoding="utf-8") as f:
            js = js_passes("CA_PASSES", f.read())
        self.assertEqual(list(R["CA_PASSES"]), [row[0] for row in js])
        for (name, label, lat, lon, elev), (key, p) in zip(js, R["CA_PASSES"].items()):
            self.assertEqual(name, key)
            self.assertEqual(label, p["label"])
            self.assertAlmostEqual(lat, p["lat"], places=4)
            self.assertAlmostEqual(lon, p["lon"], places=4)
            self.assertEqual(elev, p["elev_ft"])

    def test_viewer_draws_pass_readouts_and_skips_wave_inland_layer(self):
        with open(VIEWER, encoding="utf-8") as f:
            v = f.read()
        with open(SEL, encoding="utf-8") as f:
            sel = f.read()
        self.assertIn("function drawPassLabels", v)
        self.assertIn("WXSelect.showStaticTowns", v)
        self.assertIn("addCoastalTowns", v)
        self.assertIn("hiw: [350, 1.5, 40]", v)
        self.assertNotIn("SCREEN_IN", v)
        self.assertNotIn("formatValidPT", sel)


if __name__ == "__main__":
    unittest.main()
