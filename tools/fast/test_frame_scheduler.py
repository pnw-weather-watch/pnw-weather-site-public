"""Fair scheduler: short turns, per-model locks, preview crops, and a live switch that defaults off."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import frame_scheduler as fs
import fast_cycle as fc
from upload_r2 import Prefixed
from test_preview_publish import FakeRaw


class Plan(unittest.TestCase):
    def test_poll_is_inside_the_minute_and_turns_are_fair(self):
        self.assertGreaterEqual(fs.POLL_SECONDS, 30)
        self.assertLessEqual(fs.POLL_SECONDS, 60)
        self.assertEqual(fs.cadence("hrrr"), "hour")
        self.assertEqual(fs.cadence("epsm"), "member")
        self.assertEqual(fs.cadence("aensm"), "member")
        self.assertEqual(fs.cadence("oisst"), "daily")
        self.assertEqual(fs.slice_span("hrrr", 2), fs.SLICE_MINUTES)
        self.assertEqual(fs.slice_span("epsm", 2), 8)
        self.assertEqual(fs.slice_span("oisst", 2), 8)
        self.assertEqual(fs.slice_span("hrrr", 10), 10)
        paused = {"ifs9"}
        turns = fs.plan(["hrrr", "gfs", "ifs9", "oisst"], paused, mem_kb=8_000_000)
        self.assertEqual([m for m, _ in turns], ["hrrr", "gfs", "oisst"])
        self.assertTrue(all(w <= 2 for _, w in turns))

    def test_ifs9_needs_memory_and_then_one_worker(self):
        self.assertEqual(fs.mem_available_kb("MemTotal: 100\nMemAvailable: 5000000 kB\n"), 5000000)
        self.assertIsNone(fs.mem_available_kb(""))
        self.assertEqual(fs.workers_for("ifs9", 3_000_000), 0)
        self.assertEqual(fs.workers_for("ifs9", 8_000_000), 1)
        self.assertEqual(fs.workers_for("ifs9", None), 0)
        self.assertEqual(fs.workers_for("hrrr", 1_000_000, requested=4), 2)

    def test_hourly_turn_outlasts_the_encoder_reserve(self):
        """fast_cycle.one() prints 'time budget used up' when under 120 seconds remain."""
        self.assertGreater(fs.SLICE_MINUTES, fs.ENCODER_RESERVE_MINUTES)
        self.assertGreater(fs.slice_span("hrrr", fs.SLICE_MINUTES), fs.ENCODER_RESERVE_MINUTES)
        self.assertGreaterEqual(fs.slice_span("epsm", fs.SLICE_MINUTES), fs.MEMBER_SLICE_MINUTES)
        deadline = 10_000.0
        self.assertTrue(fs.turn_fits(fs.SLICE_MINUTES, deadline - fs.SLICE_MINUTES * 60, deadline))
        self.assertFalse(fs.turn_fits(fs.SLICE_MINUTES, deadline - fs.SLICE_MINUTES * 60 + 1, deadline))
        self.assertFalse(fs.turn_fits(fs.SLICE_MINUTES, deadline - fs.ENCODER_RESERVE_MINUTES * 60, deadline))

    def test_carry_over_starts_with_models_that_missed_a_turn(self):
        models = ["hrrr", "rrfs", "nbm", "gfs", "ifs"]
        served = ["hrrr", "rrfs", "nbm"]
        more = {"hrrr", "rrfs", "nbm", "gfs", "ifs"}
        self.assertEqual(fs.next_models(models, served, more), ["gfs", "ifs", "hrrr", "rrfs", "nbm"])
        self.assertEqual(fs.next_models(models, served, {"gfs", "ifs"}), ["gfs", "ifs"])
        self.assertEqual(fs.next_models(models, served, {"hrrr"}), ["hrrr"])
        self.assertEqual(fs.next_models(models, served, set()), [])

    def test_rrfsna_stays_last_on_carry_over(self):
        """A due rrfsna cycle must not jump ahead of HRRR/GFS even if it missed a turn."""
        self.assertEqual(fs.cadence("rrfsna"), "hour")
        self.assertEqual(fs.slice_span("rrfsna", 2), fs.SLICE_MINUTES)
        self.assertEqual(fs.DEFAULT_MODELS[-1], "rrfsna")
        models = ["hrrr", "rrfs", "rrfsna", "nbm", "gfs"]
        served = ["hrrr", "rrfs"]
        more = {"hrrr", "rrfs", "rrfsna", "nbm", "gfs"}
        self.assertEqual(fs.next_models(models, served, more), ["nbm", "gfs", "hrrr", "rrfs", "rrfsna"])
        self.assertEqual(fs.next_models(models, served, {"rrfsna", "nbm"}), ["nbm", "rrfsna"])

    def test_redispatch_keeps_the_prefix_and_the_model_list(self):
        args = fs.redispatch_args(["gfs", "ifs", "hrrr"], 20, "preview-pr19/")
        self.assertIn("models=gfs,ifs,hrrr", args)
        self.assertIn("prefix=preview-pr19/", args)
        self.assertIn("promote=false", args)

    def test_a_second_lock_does_not_steal_the_model(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = fs.ModelLock("hrrr", d), fs.ModelLock("hrrr", d)
            self.assertTrue(a.acquire())
            self.assertFalse(b.acquire())
            a.release()
            self.assertTrue(b.acquire())
            b.release()


class CropsAndLive(unittest.TestCase):
    def test_preview_takes_the_live_wide_crops_and_hides_old_runs(self):
        preview = {"models": {"hrrr": {"crop": [1, 2, 3, 4], "grid": "lcc"}, "gfs": {"crop": [0, 1, 0, 1]}},
                   "runs": {"hrrr": ["old", "new"], "gfs": ["g"]}}
        wide = [0, 10, -2, 8]
        live = {"models": {
            "hrrr": {"name": "H", "crop": wide, "grid": "lcc", "views": {"pnwwide": {}}},
            "rrfs": {"name": "R", "crop": wide, "grid": "lcc"},
            "ifs9": {"name": "I", "crop": [1, 2, 3, 4], "grid": "ll"},
        }}
        grids = {("hrrr", "new"): {"ny": 10, "nx": 10, "i0": 0, "j0": -2}}
        out = fc.align_preview_manifest(preview, live, grids)
        self.assertEqual(out["models"]["hrrr"]["crop"], wide)
        self.assertIn("pnwwide", out["models"]["hrrr"]["views"])
        self.assertEqual(out["runs"]["hrrr"], ["new"])
        self.assertEqual(out["models"]["gfs"]["crop"], [0, 1, 0, 1])
        self.assertEqual(out["runs"]["gfs"], ["g"])
        self.assertEqual(out["models"]["ifs9"]["grid"], "ll")
        self.assertEqual(out["runs"]["ifs9"], [])

    def test_live_copy_stays_off_and_refuses_a_shifted_grid(self):
        raw = FakeRaw()
        crop = [0, 10, -2, 8]
        raw.store["manifest.json"] = (json.dumps({"models": {"hrrr": {"name": "H", "site": "H", "res": "3 km", "grid": "lcc", "crop": crop}}, "runs": {"hrrr": []}}).encode(), "L")
        rel = "runs/hrrr/2026110812/single/t2m_f001.webp"
        raw.store["preview/" + rel] = (b"webp", "p")
        raw.store["preview/runs/hrrr/2026110812/run.json"] = (b"{}", "p")
        s3 = Prefixed(raw, "preview/")
        built = {"cycle": "2026110812", "grid": {"ny": 10, "nx": 10, "i0": 0, "j0": -2}, "model": "hrrr"}
        os.environ.pop("WX_LIVE_PUBLISH", None)
        self.assertFalse(fc.copy_verified_live(s3, [rel], built, "hrrr"))
        self.assertNotIn(rel, raw.store)
        os.environ["WX_LIVE_PUBLISH"] = "1"
        try:
            bad = {"cycle": "2026110812", "grid": {"ny": 5, "nx": 5, "i0": 0, "j0": 0}}
            self.assertFalse(fc.copy_verified_live(s3, [rel], bad, "hrrr"))
            self.assertNotIn(rel, raw.store)
            fc.copy_verified_live(s3, [rel, "runs/hrrr/2026110812/run.json"], built, "hrrr")
        finally:
            os.environ.pop("WX_LIVE_PUBLISH", None)
        self.assertEqual(raw.store[rel][0], b"webp")
        self.assertIn("preview/" + rel, raw.store)
        man = json.loads(raw.store["manifest.json"][0])
        self.assertEqual(man["runs"]["hrrr"], ["2026110812"])
        self.assertEqual(json.loads(raw.store["manifest.index.json"][0])["catalog_v"], 1)
        self.assertIn("models/hrrr.json", raw.store)


if __name__ == "__main__":
    unittest.main()
