import os, json, tempfile, unittest
from pathlib import Path
import ens_member_check as EMC

N = list(range(1, 51))


def mem_doc(num=None, extra_fields=None):
    num = dict(num or {k: list(N) for k in ("msl", "2t")})
    v = {k: [[i] for i in range(len(arr))] for k, arr in num.items()}
    if extra_fields:
        v.update(extra_fields)
    return {"n": ["Seattle"], "s": {k: 10 for k in num}, "v": v, "num": num}


def ens_doc(mnum=None, n=50):
    mnum = list(mnum if mnum is not None else N)
    lows = [[k, 10, 20, 990.0 + k] for k in range(min(5, len(mnum)))]
    return {"n": n, "lows": lows, "mnum": mnum, "spag": {}}


class Numbers(unittest.TestCase):
    def test_exact_1_to_50(self):
        ok, issues = EMC.check_numbers(N)
        self.assertTrue(ok, issues)

    def test_missing_and_duplicate(self):
        xs = list(N); xs[7] = 1
        ok, issues = EMC.check_numbers(xs)
        self.assertFalse(ok)
        self.assertTrue(any("missing" in i or "duplicates" in i for i in issues))

    def test_control_stays_separate(self):
        ok, issues = EMC.check_numbers([0] + N)
        self.assertFalse(ok)
        self.assertTrue(any("unexpected" in i for i in issues))
        ok, issues = EMC.check_numbers([0] + N, allow_control=True)
        self.assertTrue(ok, issues)

    def test_shuffled_file_order_is_not_enough(self):
        # Presence of 1..50 in some other order still passes check_numbers
        # (the encoder sorts by number). A gap must fail.
        ok, _ = EMC.check_numbers(list(reversed(N)))
        self.assertTrue(ok)
        ok, _ = EMC.check_numbers(N[:-1])
        self.assertFalse(ok)


class Documents(unittest.TestCase):
    def test_mem_json_ok(self):
        ok, issues = EMC.check_mem_json(mem_doc())
        self.assertTrue(ok, issues)

    def test_mem_json_requires_all_fifty_per_field(self):
        d = mem_doc(num={"msl": list(N), "2t": list(N[:40])})
        ok, issues = EMC.check_mem_json(d)
        self.assertFalse(ok)
        self.assertTrue(any("2t" in i for i in issues))

    def test_mem_json_missing_num(self):
        ok, issues = EMC.check_mem_json({"n": [], "v": {}})
        self.assertFalse(ok)

    def test_ens_json_ok(self):
        ok, issues = EMC.check_ens_json(ens_doc())
        self.assertTrue(ok, issues)

    def test_ens_json_bad_mnum(self):
        ok, issues = EMC.check_ens_json(ens_doc(mnum=list(range(50))))  # 0..49
        self.assertFalse(ok)

    def test_run_members(self):
        ok, _ = EMC.check_run_members({"members": N})
        self.assertTrue(ok)
        ok, _ = EMC.check_run_members({"members": N[:49]})
        self.assertFalse(ok)


class FilesAndPoint(unittest.TestCase):
    def test_byte_identical_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for n in N:
                p = os.path.join(td, f"m{n:02d}.bin")
                open(p, "wb").write(b"same" if n in (12, 24) else bytes([n]))
                paths.append(p)
            ok, issues = EMC.check_files_unique(paths)
            self.assertFalse(ok)
            self.assertTrue(any("byte-identical" in i for i in issues))

    def test_unique_files_pass(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for n in N:
                p = os.path.join(td, f"m{n:02d}.bin")
                open(p, "wb").write(bytes([n]))
                paths.append(p)
            ok, issues = EMC.check_files_unique(paths)
            self.assertTrue(ok, issues)

    def test_point_match_by_number(self):
        raw = {n: 1000.0 + n / 10.0 for n in N}
        stored = dict(raw)
        ok, issues = EMC.check_point_match(stored, raw, tol=0.15, name="msl")
        self.assertTrue(ok, issues)
        stored[24] = raw[1]  # pair member 24 with member 1's value
        ok, issues = EMC.check_point_match(stored, raw, tol=0.15, name="msl")
        self.assertFalse(ok)
        self.assertTrue(any("member 24" in i for i in issues))


class PromoteGate(unittest.TestCase):
    def test_non_ensemble_passes(self):
        ok, why = EMC.member_promote_ok("hrrr", {"complete": True})
        self.assertTrue(ok, why)

    def test_epsm_requires_1_to_50(self):
        ok, why = EMC.member_promote_ok("epsm", {"members": N})
        self.assertTrue(ok, why)
        ok, why = EMC.member_promote_ok("epsm", {"members": N[:40]})
        self.assertFalse(ok)
        self.assertIn("missing", why)

    def test_member_check_flag_blocks_promote(self):
        cand = {"members": N, "member_check": {"ok": False, "issues": ["mslp: member 7 stored=1 raw=2"]}}
        ok, why = EMC.member_promote_ok("aensm", cand)
        self.assertFalse(ok)
        self.assertIn("member_check failed", why)

    def test_eps_inspects_mem_and_ens(self):
        steps = [{"f": 12}, {"f": 24}, {"f": 36}]
        cand = {"cycle": "2026110912", "steps": steps}
        store = {
            "runs/eps/2026110912/single/mem_f012.json": mem_doc(),
            "runs/eps/2026110912/single/ens_f012.json": ens_doc(),
            "runs/eps/2026110912/single/mem_f024.json": mem_doc(),
            "runs/eps/2026110912/single/ens_f024.json": ens_doc(),
            "runs/eps/2026110912/single/mem_f036.json": mem_doc(),
            "runs/eps/2026110912/single/ens_f036.json": ens_doc(),
        }
        ok, why = EMC.member_promote_ok("eps", cand, fetch_json=store.get)
        self.assertTrue(ok, why)
        store["runs/eps/2026110912/single/mem_f024.json"] = mem_doc(num={"msl": N[:49], "2t": N})
        ok, why = EMC.member_promote_ok("eps", cand, fetch_json=store.get)
        self.assertFalse(ok)

    def test_eps_trusts_passing_member_check(self):
        cand = {"cycle": "2026110912", "steps": [{"f": 6}], "member_check": {"ok": True}}
        ok, why = EMC.member_promote_ok("eps", cand)
        self.assertTrue(ok, why)


class EncodedRun(unittest.TestCase):
    def test_check_encoded_run_epsm(self):
        with tempfile.TemporaryDirectory() as td:
            run = {"model": "epsm", "members": N, "steps": [{"f": 24}]}
            json.dump(run, open(os.path.join(td, "run.json"), "w"))
            for n in N:
                d = os.path.join(td, f"m{n:02d}"); os.makedirs(d)
                open(os.path.join(d, "mem_f024.webp"), "wb").write(bytes([n]) * 8)
            report = EMC.check_encoded_run(td, "epsm")
            self.assertTrue(report["ok"], report)



RUNNER = "/home/runner/work/pnw-weather-site-public/pnw-weather-site-public/tools/fast/data"


def r2_store(model="eps", cyc="2026111100", steps=(3, 75, 144)):
    s = {}
    for f in steps:
        s[f"runs/{model}/{cyc}/single/mem_f{f:03d}.json"] = mem_doc()
        s[f"runs/{model}/{cyc}/single/ens_f{f:03d}.json"] = ens_doc()
    return s


def runner_stamp(model, cyc, steps):
    return {"ok": False, "checked": [], "issues": [
        f"missing {RUNNER}/runs/{model}/{cyc}/single/{k}_f{f:03d}.json" for f in steps for k in ("mem", "ens")]}


class MembersFromR2(unittest.TestCase):
    """Stamps written on the runner after its step files were uploaded and deleted (Nov 11 3 AM check)."""

    def test_files_only_in_r2_pass_the_promote_gate(self):
        for model in ("eps", "aens"):
            steps = [{"f": 3}, {"f": 75}, {"f": 144}]
            cand = {"cycle": "2026111100", "steps": steps, "member_check": runner_stamp(model, "2026111100", (3, 75, 144))}
            ok, why = EMC.member_promote_ok(model, cand, fetch_json=r2_store(model).get)
            self.assertTrue(ok, why)
            self.assertIn("R2", why)

    def test_files_only_in_r2_pass_the_encode_stamp(self):
        with tempfile.TemporaryDirectory() as td:   # nothing on local disk
            run = {"cycle": "2026111100", "steps": [{"f": 3}, {"f": 75}, {"f": 144}]}
            report = EMC.check_encoded_run(td, "eps", fetch_json=r2_store().get, run=run)
            self.assertTrue(report["ok"], report)
            self.assertEqual(len(report["checked"]), 6)

    def test_real_mismatch_in_r2_fails(self):
        store = r2_store("aens")
        store["runs/aens/2026111100/single/mem_f075.json"] = mem_doc(num={"msl": N[:49] + [49], "2t": N})
        cand = {"cycle": "2026111100", "steps": [{"f": 3}, {"f": 75}, {"f": 144}],
                "member_check": runner_stamp("aens", "2026111100", (3, 75, 144))}
        ok, why = EMC.member_promote_ok("aens", cand, fetch_json=store.get)
        self.assertFalse(ok)
        self.assertIn("msl", why)
        store = r2_store()
        store["runs/eps/2026111100/single/ens_f144.json"] = ens_doc(mnum=N[:-1] + [0])
        with tempfile.TemporaryDirectory() as td:
            report = EMC.check_encoded_run(td, "eps", fetch_json=store.get,
                                           run={"cycle": "2026111100", "steps": [{"f": 3}, {"f": 75}, {"f": 144}]})
            self.assertFalse(report["ok"])

    def test_real_mismatch_in_stamp_still_blocks(self):
        stamp = runner_stamp("eps", "2026111100", (3,))
        stamp["issues"].append("msl: missing [7]")
        cand = {"cycle": "2026111100", "steps": [{"f": 3}], "member_check": stamp}
        ok, why = EMC.member_promote_ok("eps", cand, fetch_json=r2_store(steps=(3,)).get)
        self.assertFalse(ok)
        self.assertIn("msl: missing [7]", why)

    def test_missing_files_fail(self):
        store = r2_store()
        del store["runs/eps/2026111100/single/ens_f075.json"]
        cand = {"cycle": "2026111100", "steps": [{"f": 3}, {"f": 75}, {"f": 144}],
                "member_check": runner_stamp("eps", "2026111100", (3, 75, 144))}
        ok, why = EMC.member_promote_ok("eps", cand, fetch_json=store.get)
        self.assertFalse(ok)
        self.assertIn("missing ens_f075.json", why)
        with tempfile.TemporaryDirectory() as td:
            report = EMC.check_encoded_run(td, "eps", fetch_json=store.get,
                                           run={"cycle": "2026111100", "steps": [{"f": 3}, {"f": 75}, {"f": 144}]})
            self.assertFalse(report["ok"])
            self.assertTrue(any("ens_f075" in i for i in report["issues"]))
            report = EMC.check_encoded_run(td, "eps", run={"cycle": "2026111100", "steps": [{"f": 3}]})
            self.assertFalse(report["ok"])   # no R2 reader and nothing local: still fails

    def test_local_only_stamp_without_r2_reader_does_not_pass(self):
        cand = {"cycle": "2026111100", "steps": [{"f": 3}], "member_check": runner_stamp("eps", "2026111100", (3,))}
        ok, why = EMC.member_promote_ok("eps", cand)
        self.assertFalse(ok)


class Labels(unittest.TestCase):
    def test_aifs_wind_labeled_instantaneous(self):
        src = Path(__file__).with_name("fast_encode.py").read_text(encoding="utf-8")
        self.assertIn("instantaneous 10 m wind (no gust field)", src)
        self.assertIn("instantaneous 10 m wind", src)
        self.assertIn("ECMWF gust window (1/3/6 h)", src)


if __name__ == "__main__":
    unittest.main()
