"""Every encoded model publishes the same high-res Pacific Northwest view.

static() copies regions.json model_views onto the model, then writes one color key
per (product, view). Live and preview use those same key names (preview/<key> first).
The window itself is the existing pnwhr frame: global models crop it from their native grid.
"""
import inspect
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "forecast"))
import fast_encode as fe
import regions

REGIONS = os.path.normpath(os.path.join(HERE, "..", "..", "regions", "regions.json"))

# Globals and NBM. 150 mi west of -116.4. Same size, same edge latitudes.
PNWHR = {
    "label": "Pacific NW (high-res)",
    "proj": ["lcc", -119.5, 45.7, [42, 49]],
    "ll": [-131.41, -107.59, 41.7, 49.7],
}
HIRES = {
    "proj": ["lcc", -116.69, 45.7, [42, 49]],
    "ll": [-128.6, -104.78, 41.7, 49.7],
}


class PnwhrViews(unittest.TestCase):
    def test_one_window_and_every_model_lists_it(self):
        with open(REGIONS) as f:
            R = json.load(f)
        v = R["views"]["pnwhr"]
        for k, want in PNWHR.items():
            self.assertEqual(v[k], want, k)
        for k, want in HIRES.items():
            self.assertEqual(v["hires"][k], want, k)
        self.assertEqual(v["extent"], v["hires"]["extent"])
        self.assertEqual(list(R["views"]).count("pnwhr"), 1)
        self.assertEqual(R["views"]["pnwwide"]["label"], "Pacific Northwest (Wide)")
        missing = [m for m, vs in R["model_views"].items() if "pnwhr" not in vs]
        self.assertEqual(missing, [])
        # The wide frame is on every model, including HRRR, RRFS and the 9 km job.
        for m in R["model_views"]:
            self.assertIn("pnwwide", R["model_views"][m], m)
        # The encoder's model table is the same set the static job publishes.
        self.assertEqual(set(fe.MODELS), set(R["model_views"]))
        for m in fe.MODELS:
            self.assertIn("pnwhr", regions.R["model_views"][m], m)

    def test_static_publishes_a_key_for_that_view(self):
        # regions.apply copies model_views onto MODELS before static reads them,
        # and the key file name includes the view id (live and preview share the name).
        apply = inspect.getsource(regions.apply)
        self.assertIn('FE.MODELS[m]["views"] = tuple(vs)', apply)
        static = inspect.getsource(fe.static)
        self.assertLess(static.index("extra_views(TM, ccrs)"), static.index('vids = MD["views"]'))
        self.assertIn("fn = product_key(m, pid, vid, kv)", static)
        self.assertIn('P["keys"][vid] = fn', static)
        self.assertIn("_{vid}.png", inspect.getsource(fe.product_key))


if __name__ == "__main__":
    unittest.main()
