import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto_promote_live as A
CROP = [216, 1139, -277, 973]
G = {"ny": 923, "nx": 1250, "i0": 216, "j0": -277}
def run(n, complete=False, grid=G, start=1):
    return {"grid": grid, "steps": [{"f": f} for f in range(start, start + n)], "complete": complete, "expected": 48}
class T(unittest.TestCase):
    def test_newer_complete(self):
        self.assertTrue(A.decide("hrrr", "2026110812", run(48, True), ["2026110806"], run(2), CROP)[0])
    def test_newer_partial_more(self):
        self.assertTrue(A.decide("hrrr", "2026110812", run(5), ["2026110806"], run(2), CROP)[0])
    def test_never_replace_fuller_with_partial(self):
        self.assertFalse(A.decide("hrrr", "2026110812", run(3), ["2026110806"], run(48, True), CROP)[0])
    def test_fill_same_run(self):
        self.assertTrue(A.decide("hrrr", "2026110806", run(30), ["2026110806"], run(2), CROP)[0])
        self.assertFalse(A.decide("hrrr", "2026110806", run(2), ["2026110806"], run(2), CROP)[0])
    def test_older(self):
        self.assertFalse(A.decide("hrrr", "2026110800", run(48, True), ["2026110806"], run(2), CROP)[0])
    def test_wrong_grid(self):
        old = {"ny": 843, "nx": 766, "i0": 216, "j0": 0}
        self.assertFalse(A.decide("hrrr", "2026110812", run(48, True, old), ["2026110806"], run(2), CROP)[0])
    def test_holes(self):
        r = run(3); r["steps"] = [{"f": 1}, {"f": 3}, {"f": 2}]
        self.assertFalse(A.decide("hrrr", "2026110812", r, ["2026110806"], run(2), CROP)[0])
    def test_manifest_keeps_list_and_progress(self):
        man = {"runs": {"ifs": ["a1", "a2", "a3", "a4", "a5", "a6"]}, "progress": {"ifs": {"a6": [12, 360]}}}
        A.apply_manifest(man, {}, "ifs", "a7", run(2), 6)
        self.assertEqual(man["runs"]["ifs"], ["a2", "a3", "a4", "a5", "a6", "a7"])
        self.assertEqual(man["progress"]["ifs"], {"a6": [12, 360], "a7": [2, 48]})
        A.apply_manifest(man, {}, "ifs", "a7", run(48, True), 6)
        self.assertNotIn("a7", man["progress"]["ifs"])
if __name__ == "__main__": unittest.main()
