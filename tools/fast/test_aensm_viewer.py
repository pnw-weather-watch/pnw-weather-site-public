"""AIFS ENS members use the same viewer path as EPS members."""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import fast_encode as FE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

class AensmViewer(unittest.TestCase):
    def test_model_entry(self):
        self.assertIn("aensm", FE.MODELS)
        md = FE.MODELS["aensm"]
        self.assertEqual(md.get("grid_from"), "aens")
        self.assertEqual(md["grid"], "ll")
        self.assertIn(6, md["steps"])
        self.assertIn(360, md["steps"])
        info = FE.minfo("aensm")
        self.assertEqual(info["site"], "AIFS ENS member")
        self.assertIn("member", info["name"].lower())

    def test_menu_order_lists_aensm_beside_epsm(self):
        text = open(os.path.join(HERE, "site", "viewer.js"), encoding="utf-8").read()
        self.assertIn('"aensm"', text)
        self.assertIn("isMemRun", text)
        self.assertIn("function memUI()", text)
        # Runs menu lists AIFS members next to EPS members
        self.assertIn('"aens", "aensm", "epsm"', text)

    def test_same_views_as_aens(self):
        r = json.load(open(os.path.join(ROOT, "regions", "regions.json")))
        self.assertEqual(r["model_views"]["aensm"], r["model_views"]["aens"])
        self.assertIn("pnwhr", r["model_views"]["aensm"])

if __name__ == "__main__":
    unittest.main()
