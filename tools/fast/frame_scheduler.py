#!/usr/bin/env python3
"""Fair, bounded publisher. One pass gives every due model a short turn, then polls again.

PR6 ran the twelve models one after another for twelve minutes each, so a late model
waited hours. This queue encodes one newly posted slice per model, locks that model,
and sleeps 45 seconds (inside the 30-60 second window) before the next round.

OISST is daily. EPS members and AIFS-ENS members publish a member-hour only when that
hour's source index is already the check inside their own tools. IFS9 stays paused
unless it is removed from FAST_PAUSED, and then it runs as one worker only when
MemAvailable is at least 4 GB.

Live copies are not part of this loop. fast_cycle writes the requested prefix.
WX_LIVE_PUBLISH=1 is the only switch that also copies a verified frame onto the live keys.

  python3 tools/fast/frame_scheduler.py --models hrrr,gfs --minutes 20 --poll 45
"""
import argparse, fcntl, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
POLL_SECONDS = 45
SLICE_MINUTES = 2
IFS9_MIN_KB = 4_000_000
HOURLY = ("hrrr", "rrfs", "nbm", "gfs", "ifs", "ifs9", "aifs", "eps", "aens", "gfsw")
MEMBERS = ("epsm", "aensm")
DAILY = ("oisst",)
OWN_SCRIPT = {"oisst": "oisst_cycle.py", "epsm": "epsm_cycle.py", "aensm": "aensm_cycle.py"}
DEFAULT_MODELS = HOURLY + MEMBERS + DAILY


def mem_available_kb(text):
    """KiB from /proc/meminfo MemAvailable, or None when the line is absent."""
    for line in (text or "").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    return None


def read_mem_available_kb():
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            return mem_available_kb(f.read())
    except OSError:
        return None


def workers_for(model, mem_kb, requested=2):
    """IFS9 is one worker, and only when memory is known to be enough. Others stay at 2."""
    if model == "ifs9":
        if mem_kb is None or mem_kb < IFS9_MIN_KB: return 0
        return 1
    if model == "oisst": return 1
    return max(1, min(int(requested), 2))


def paused_set(env=None):
    raw = (env if env is not None else os.environ).get("FAST_PAUSED", "")
    return {x.strip() for x in raw.split(",") if x.strip()}


def plan(models, paused, mem_kb, requested=2):
    """(model, workers) in the caller's order, skipping paused models and an unready IFS9."""
    out = []
    for m in models:
        if m in paused: continue
        w = workers_for(m, mem_kb, requested)
        if w <= 0: continue
        out.append((m, w))
    return out


def cadence(model):
    if model in DAILY: return "daily"
    if model in MEMBERS: return "member"
    return "hour"


def slice_span(model, slice_minutes):
    """Member tools refuse to encode inside their last 5 minutes, so they need a longer turn."""
    if cadence(model) == "hour": return slice_minutes
    return max(slice_minutes, 8)

def slice_command(model, workers, minutes):
    script = OWN_SCRIPT.get(model, "fast_cycle.py")
    cmd = [sys.executable, os.path.join(HERE, script)]
    if script == "fast_cycle.py":
        cmd += ["--models", model, "--minutes", str(minutes), "--workers", str(workers), "--every", str(POLL_SECONDS)]
    elif script != "oisst_cycle.py":
        cmd += ["--minutes", str(minutes), "--workers", str(workers)]
    return cmd


def redispatch_args(models, minutes, prefix):
    """Flags a follow-up workflow_dispatch must keep. An empty dispatch drops the prefix."""
    return ["-f", f"models={','.join(models)}", "-f", f"minutes={minutes}", "-f", f"prefix={prefix}", "-f", "promote=false"]


class ModelLock:
    """One non-blocking lock per model so a re-dispatch cannot encode the same run twice."""

    def __init__(self, model, directory):
        os.makedirs(directory, exist_ok=True)
        self.path = os.path.join(directory, model)
        self.fd = None
        self.held = False

    def acquire(self):
        self.fd = open(self.path, "a+")
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.fd.close(); self.fd = None
            return False
        self.held = True
        return True

    def release(self):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.fd.close(); self.fd = None
        self.held = False


def align_shared_preview():
    """One-time-per-pass copy of the live HRRR/RRFS/IFS9 model records onto preview/ only."""
    from upload_r2 import client
    from fast_cycle import align_preview_manifest, update_manifest, BUCKET
    s3 = client()
    if getattr(s3, "prefix", "") != "preview/": return None
    raw = getattr(s3, "raw", None)
    if raw is None: return None
    try:
        live = __import__("json").loads(raw.get_object(Bucket=BUCKET, Key="manifest.json")["Body"].read())
        preview = __import__("json").loads(s3.get_object(Bucket=BUCKET, Key="manifest.json")["Body"].read())
    except Exception as e:
        print("preview crop align skipped:", e, flush=True)
        return None
    grids = {}
    for m in ("hrrr", "rrfs", "ifs9"):
        for cyc in ((preview.get("runs") or {}).get(m) or []):
            try:
                run = __import__("json").loads(s3.get_object(Bucket=BUCKET, Key=f"runs/{m}/{cyc}/run.json")["Body"].read())
            except Exception:
                continue
            if run.get("grid"): grids[(m, cyc)] = run["grid"]
    aligned = align_preview_manifest(preview, live, grids)
    def fn(mn):
        mn.clear(); mn.update(aligned)
    update_manifest(s3, fn)
    print("preview crops aligned for hrrr, rrfs, ifs9", flush=True)
    return aligned


def _child_env():
    env = os.environ.copy()
    env.pop("GITHUB_OUTPUT", None)
    return env


def run_slice(model, workers, minutes, dry_run):
    cmd = slice_command(model, workers, minutes)
    print(" ", " ".join(cmd), flush=True)
    if dry_run: return False
    proc = subprocess.run(cmd, cwd=HERE, env=_child_env(), capture_output=True, text=True)
    sys.stdout.write(proc.stdout or "")
    sys.stderr.write(proc.stderr or "")
    more = False
    for line in (proc.stdout or "").splitlines():
        if line.startswith("more work left:") and "none" not in line:
            more = True
    return more


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--minutes", type=float, default=20)
    ap.add_argument("--poll", type=float, default=POLL_SECONDS)
    ap.add_argument("--slice-minutes", type=float, default=SLICE_MINUTES)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--lock-dir", default=os.environ.get("WX_LOCK_DIR", "/tmp/wx-model-locks"))
    a = ap.parse_args(argv)
    if not 30 <= a.poll <= 60:
        raise SystemExit(f"poll must be 30-60 s, not {a.poll}")
    models = [m for m in a.models.split(",") if m]
    paused = paused_set()
    mem = read_mem_available_kb()
    print(f"scheduler models={','.join(models)} paused={','.join(sorted(paused)) or '-'} mem_kb={mem} poll={a.poll:.0f}s", flush=True)
    if not a.dry_run:
        try: align_shared_preview()
        except Exception as e: print("preview crop align failed:", e, flush=True)
    deadline = time.time() + a.minutes * 60
    more = set()
    once = {m for m in models if cadence(m) != "hour"}
    did_once = set()
    while time.time() < deadline:
        turns = plan(models, paused, mem)
        progressed = False
        for model, workers in turns:
            if time.time() >= deadline: break
            if model in once:
                if model in did_once: continue
                did_once.add(model)
            lock = ModelLock(model, a.lock_dir)
            if not lock.acquire():
                print(f"{model}: locked, skip this turn", flush=True)
                more.add(model)
                continue
            try:
                # Member tools stop encoding inside the last 5 minutes of their budget, so a 2-minute
                # slice would publish nothing. Daily and member turns get one longer slice per pass.
                span = slice_span(model, a.slice_minutes)
                if run_slice(model, workers, span, a.dry_run): more.add(model)
                progressed = True
            finally:
                lock.release()
        if a.dry_run or time.time() + a.poll >= deadline: break
        if not progressed: break
        print(f"poll {a.poll:.0f}s", flush=True)
        time.sleep(a.poll)
    print("more work left:", ",".join(sorted(more)) or "none", flush=True)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"more={'true' if more else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
