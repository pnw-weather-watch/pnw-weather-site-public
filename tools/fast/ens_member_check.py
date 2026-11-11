#!/usr/bin/env python3
"""Ensemble member-number correctness (Weather Bot method).

Every field is keyed by the GRIB `number` attribute (cf=0 control, pf=1..50),
never by file or index position. The ECMWF open-data index lists perturbed
members in a shuffled order that changes per step and even per parameter.

Checks used at encode time and again before auto-promote:
  - numbers are exactly 1..50 (no repeats, none missing; control stays separate)
  - every written field has all 50 members (a ">= 40" gate is not enough)
  - no two member files are byte-identical
  - one raw-GRIB point compared by member number is within tolerance
"""
from __future__ import annotations

import hashlib
import json
import os

EXPECTED = list(range(1, 51))
CONTROL = 0
# Seattle (KSEA) slot on the shared 0.25 deg EPS/AENS crop [8, 367, 484, 1421]
SEATTLE = {"name": "Seattle", "fi": 161.6, "fj": 466.74}
# Stored MSLP is tenths of a millibar; gusts are whole mph (rounded).
TOL_MSL_TENTHS = 1
TOL_GUST_MPH = 1
TOL_MSLP_MB = 1.0
MEMBER_MODELS = ("eps", "aens", "epsm", "aensm")


def _as_ints(nums):
    out = []
    for n in nums or []:
        try:
            out.append(int(n))
        except (TypeError, ValueError):
            out.append(n)
    return out


def check_numbers(nums, *, name="members", allow_control=False):
    """Return (ok, issues). `nums` is the GRIB `number` of each row or file."""
    xs = _as_ints(nums)
    expected = ([CONTROL] + EXPECTED) if allow_control else EXPECTED
    issues = []
    if any(not isinstance(n, int) for n in xs):
        issues.append(f"{name}: non-integer member number in {xs[:8]}")
        return False, issues
    missing = [n for n in expected if n not in xs]
    extra = [n for n in xs if n not in expected]
    dups = sorted({n for n in xs if xs.count(n) > 1})
    if missing:
        issues.append(f"{name}: missing {missing[:12]}{'...' if len(missing) > 12 else ''}")
    if extra:
        issues.append(f"{name}: unexpected {extra[:12]}")
    if dups:
        issues.append(f"{name}: duplicates {dups}")
    if len(xs) != len(expected) and not (missing or extra or dups):
        issues.append(f"{name}: length {len(xs)} != {len(expected)}")
    return not issues, issues


def check_fields_complete(num_by_field, *, required=None):
    """Every present (or required) field must have numbers exactly 1..50."""
    issues = []
    fields = list(required) if required is not None else list(num_by_field or {})
    if not fields:
        issues.append("no member fields written")
        return False, issues
    for k in fields:
        nums = (num_by_field or {}).get(k)
        if nums is None:
            issues.append(f"{k}: field missing")
            continue
        ok, more = check_numbers(nums, name=k)
        if not ok:
            issues.extend(more)
    return not issues, issues


def check_mem_json(data):
    """Validate a mem_fFFF.json document (meteogram member rows)."""
    if not isinstance(data, dict):
        return False, ["mem json: not an object"]
    nums = data.get("num") or {}
    rows = data.get("v") or {}
    issues = []
    if not nums:
        return False, ["mem json: missing num (member numbers)"]
    ok, more = check_fields_complete(nums, required=list(nums))
    issues.extend(more)
    for k, arr in nums.items():
        got = rows.get(k)
        if not isinstance(got, list) or len(got) != len(arr):
            issues.append(f"{k}: {0 if not isinstance(got, list) else len(got)} rows != {len(arr)} numbers")
    return not issues, issues


def check_ens_json(data):
    """Validate an ens_fFFF.json document (low centres + spaghetti)."""
    if not isinstance(data, dict):
        return False, ["ens json: not an object"]
    issues = []
    mnum = data.get("mnum")
    if mnum is None:
        return False, ["ens json: missing mnum (member numbers for lows)"]
    ok, more = check_numbers(mnum, name="mnum")
    issues.extend(more)
    n = data.get("n")
    if n is not None and int(n) != 50:
        issues.append(f"ens json: n={n} != 50")
    lows = data.get("lows") or []
    if mnum:
        bad_k = [row[0] for row in lows if not (0 <= int(row[0]) < len(mnum))]
        if bad_k:
            issues.append(f"ens json: low stack index outside mnum ({bad_k[:6]})")
    return not issues, issues


def check_run_members(run):
    """Validate run.json members (epsm / aensm picker)."""
    if not isinstance(run, dict):
        return False, ["run json: not an object"]
    return check_numbers(run.get("members") or run.get("num") or [], name="members")


def check_files_unique(paths):
    """Fail if two member files are byte-identical (same weather copied twice)."""
    issues = []
    seen = {}
    for p in paths:
        if not p or not os.path.isfile(p):
            issues.append(f"missing member file {p}")
            continue
        with open(p, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        seen.setdefault(h, []).append(p)
    for h, group in seen.items():
        if len(group) > 1:
            names = [os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p) for p in group]
            issues.append(f"byte-identical member files: {names}")
    return not issues, issues


def check_point_match(stored_by_num, raw_by_num, *, tol, name="point"):
    """Compare stored vs raw-GRIB values keyed by member number."""
    issues = []
    ok_n, more = check_numbers(list(raw_by_num), name=f"{name} raw")
    issues.extend(more)
    for n in EXPECTED:
        st = stored_by_num.get(n)
        rw = raw_by_num.get(n)
        if st is None or rw is None:
            issues.append(f"{name}: member {n} stored={st} raw={rw}")
            continue
        try:
            if abs(float(st) - float(rw)) > float(tol):
                issues.append(f"{name}: member {n} stored={st} raw={rw} (tol {tol})")
        except (TypeError, ValueError):
            issues.append(f"{name}: member {n} non-numeric stored={st} raw={rw}")
    return not issues, issues


def is_local_only_issue(issue):
    """True for an issue that only says a file was not on the encoder's local disk.

    The runner deletes each step file after uploading it to R2, so an encode-time
    stamp built from local files reported every uploaded hour as missing. Those
    issues say nothing about member numbers; real mismatches never look like this.
    """
    s = str(issue)
    return s.startswith("missing /") or s.startswith("missing member file") or s == "no steps to check"


def _load_json(local_path, rel_key, fetch_json):
    """Local file first (just encoded), then R2 (already uploaded and removed locally)."""
    if os.path.isfile(local_path):
        with open(local_path) as fh:
            return json.load(fh)
    if fetch_json is not None:
        return fetch_json(rel_key)
    return None


def check_encoded_run(rd, model, *, sample=3, fetch_json=None, run=None):
    """Inspect mem/ens JSON or member files for a run.

    `fetch_json(rel_key)` reads `runs/{model}/{cycle}/...` from R2 (under the
    writer's preview prefix) for step files that are no longer on local disk.
    """
    issues = []
    checked = []
    run_path = os.path.join(rd, "run.json")
    if run is None:
        run = json.load(open(run_path)) if os.path.isfile(run_path) else {}
    cyc = run.get("cycle") or os.path.basename(os.path.normpath(rd))
    base = f"runs/{model}/{cyc}"
    steps = [s.get("f") for s in (run.get("steps") or []) if "f" in s]
    if model in ("epsm", "aensm"):
        ok, more = check_run_members(run)
        issues.extend(more)
        fname = "mx" if model == "aensm" else "mem"
        pick = steps[:1] + steps[len(steps) // 2:len(steps) // 2 + 1] + steps[-1:] if steps else []
        pick = list(dict.fromkeys(pick))[:sample]
        for f in pick:
            paths = [os.path.join(rd, f"m{n:02d}", f"{fname}_f{f:03d}.webp") for n in EXPECTED]
            ok, more = check_files_unique(paths)
            issues.extend(more)
            checked.append(f"files f{f:03d}")
    elif model in ("eps", "aens"):
        pick = steps[:1] + steps[len(steps) // 2:len(steps) // 2 + 1] + steps[-1:] if steps else []
        pick = list(dict.fromkeys(pick))[:sample]
        if not pick:
            issues.append("no steps to check")
        for f in pick:
            for kind, checker in (("mem", check_mem_json), ("ens", check_ens_json)):
                name = f"{kind}_f{f:03d}.json"
                doc = _load_json(os.path.join(rd, "single", name), f"{base}/single/{name}", fetch_json)
                if doc is None:
                    issues.append(f"missing {name} (local and R2)" if fetch_json else f"missing {os.path.join(rd, 'single', name)}")
                    continue
                ok, more = checker(doc)
                issues.extend(more)
                checked.append(name[:-5])
    report = {"ok": not issues, "issues": issues, "checked": checked}
    return report


def member_promote_ok(model, cand, fetch_json=None):
    """Gate used by auto_promote_live. `fetch_json(rel_key)` loads preview JSON or None."""
    if model not in MEMBER_MODELS:
        return True, "not an ensemble-member model"
    if not cand:
        return False, "no preview run.json"
    flagged = (cand.get("member_check") or {})
    stale_stamp = False
    if flagged.get("ok") is False:
        why = flagged.get("issues") or ["member_check failed"]
        real = [x for x in why if not is_local_only_issue(x)]
        if real or not flagged.get("issues"):
            return False, "member_check failed: " + "; ".join(str(x) for x in (real or why)[:6])
        # Stamp only says files were gone from the runner's disk: re-check from R2 below.
        stale_stamp = True
    if model in ("epsm", "aensm"):
        ok, issues = check_run_members(cand)
        if not ok:
            return False, "; ".join(issues)
        return True, "members 1..50"
    # eps / aens: trust a passing encode-time stamp, otherwise inspect mem/ens JSON
    if flagged.get("ok") is True:
        return True, "member_check ok"
    if fetch_json is None:
        return False, ("member_check stamp was local-only; R2 inspection required" if stale_stamp
                       else "eps/aens promote needs mem/ens inspection or member_check")
    cyc = cand.get("cycle")
    if not cyc:
        return False, "run.json missing cycle"
    steps = cand.get("steps") or []
    if not steps:
        return False, "no steps"
    pick = [steps[0], steps[len(steps) // 2], steps[-1]]
    seen = set()
    issues = []
    for s in pick:
        f = s.get("f")
        if f in seen:
            continue
        seen.add(f)
        mem = fetch_json(f"runs/{model}/{cyc}/single/mem_f{f:03d}.json")
        ens = fetch_json(f"runs/{model}/{cyc}/single/ens_f{f:03d}.json")
        if mem is None:
            issues.append(f"missing mem_f{f:03d}.json")
        else:
            ok, more = check_mem_json(mem)
            issues.extend(more)
        if ens is None:
            issues.append(f"missing ens_f{f:03d}.json")
        else:
            ok, more = check_ens_json(ens)
            issues.extend(more)
    if issues:
        return False, "; ".join(issues[:8])
    return True, "mem/ens numbers 1..50 (read from R2)"


def report(ok, issues, **extra):
    out = {"ok": bool(ok), "issues": list(issues or [])}
    out.update(extra)
    return out
