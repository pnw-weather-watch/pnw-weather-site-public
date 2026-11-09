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

    def test_aensm_catalog_crop_copied_from_aens(self):
        man = {"models": {"aens": {"crop": [8, 361, 560, 1421]}}}
        crop = A.ensure_catalog_crop(man, "aensm")
        self.assertEqual(crop, [8, 361, 560, 1421])
        self.assertEqual(man["models"]["aensm"]["crop"], [8, 361, 560, 1421])
        # already set: do not overwrite
        man["models"]["aens"]["crop"] = [0, 1, 0, 1]
        self.assertEqual(A.ensure_catalog_crop(man, "aensm"), [8, 361, 560, 1421])

    def test_aensm_crop_can_come_from_preview_manifest(self):
        man = {"models": {}}
        prev = {"models": {"aens": {"crop": [10, 20, 30, 40]}}}
        self.assertEqual(A.ensure_catalog_crop(man, "aensm", prev), [10, 20, 30, 40])

    def test_epsm_and_oisst_donors(self):
        man = {"models": {"eps": {"crop": [1, 2, 3, 4]}, "gfs": {"crop": [5, 6, 7, 8]}}}
        self.assertEqual(A.ensure_catalog_crop(man, "epsm"), [1, 2, 3, 4])
        self.assertEqual(A.ensure_catalog_crop(man, "oisst"), [5, 6, 7, 8])

    def test_aensm_run_grid_matches_donor_crop(self):
        crop = [8, 361, 560, 1421]
        g = {"ny": 353, "nx": 861}   # aensm run.json records size only, not i0/j0
        cand = {"grid": g, "steps": [{"f": 6}], "complete": True, "expected": 60}
        self.assertTrue(A.same_grid(cand, crop))
        self.assertTrue(A.decide("aensm", "2026110900", cand, [], None, crop)[0])

    def test_apply_manifest_writes_aensm_crop(self):
        man = {"models": {"aens": {"crop": [8, 361, 560, 1421]}}}
        prev = {}
        cand = {"grid": {"ny": 353, "nx": 861}, "steps": [{"f": 6}], "complete": True, "expected": 60}
        A.apply_manifest(man, prev, "aensm", "2026110900", cand, 2)
        self.assertEqual(man["models"]["aensm"]["crop"], [8, 361, 560, 1421])
        self.assertEqual(man["runs"]["aensm"], ["2026110900"])

    def test_member_gate_blocks_short_ensemble(self):
        import ens_member_check as EMC
        ok, why = EMC.member_promote_ok("epsm", {"members": list(range(1, 41))})
        self.assertFalse(ok)
        ok, why = EMC.member_promote_ok("epsm", {"members": list(range(1, 51))})
        self.assertTrue(ok, why)
if __name__ == "__main__": unittest.main()
