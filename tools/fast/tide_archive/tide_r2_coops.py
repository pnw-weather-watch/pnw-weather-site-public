#!/usr/bin/env python3
"""Shared CO-OPS series store for the preview precompute path.

The 30-day predictions / water_level / air_pressure (and mdapi meta) the Tides
page needs live under a preview R2 prefix (default tide/precompute-preview/coops/).
Ingest appends only new hours. The headless builder reads these files and must
not call CO-OPS. Production prefix tide/v1/ is refused.
"""
from __future__ import annotations
import datetime as D, json, os, re, time, urllib.error, urllib.parse, urllib.request

HR = 3600000
DAY = 86400000
SLOW_DAYS = 30
KEEP_PAST = 32 * DAY          # 30-day residual window plus a small margin
PRED_LEAD = 8 * DAY           # default chart goes ~7 d + 3 h ahead
WL_LEAD = 6 * 60000
AIR_LEAD = HR
# Re-fetch a little history so NOAA QC revisions merge. water_level often gets
# 0.001 ft edits over the following day, so that product uses a 36 h overlap
# (still one short datagetter call). Predictions and hourly pressure stay at 2 h.
OVERLAP = 2 * HR
OVERLAP_WL = 36 * HR
API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
MD = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
UA = "pnw-weather-tides (https://github.com/pnw-weather-watch/pnw-weather-site-public; incremental coops store)"
BUCKET = os.environ.get("R2_BUCKET", "pnw-models-data")
ALLOWED = ("tide/precompute-preview/", "tide/preview/")
# tide-archive cron is "20 2,8,14,20 * * *"; the job may run up to 120 minutes.
# Ingest must not start in [HH:15, HH+2:20) UTC for those hours.
ARCHIVE_HOURS = (2, 8, 14, 20)
BLACKOUT_BEFORE_MIN = 15
BLACKOUT_AFTER_MIN = 2 * 60 + 20  # 2 h 20 min after the hour (covers 20 past + 120 min timeout)

# NOAA station ids (30 unique gauges; Birch Bay shares Cherry Point 9449424).
STATIONS = [
    "9439040", "9440581", "9449424", "9449880", "9442396", "9443090", "9444090",
    "9444900", "9447130", "9446484", "9440910", "9441102",
    "9414750", "9416841", "9419750", "9410230", "9410678", "9410660", "9415102",
    "9413450", "9418767", "9415020", "9415144", "9412110", "9414523", "9414863",
    "9410170", "9414290", "9411340", "9410840",
]
# Gauges with no (or unused) own barometer still need neighbor series on disk.
P_NEIGHBORS = {
    "9439040": ["9440581", "9440910", "9441102", "9446484"],
    "9440581": ["9439040", "9440910", "9441102", "9446484"],
    "9410678": ["9410660", "9410840", "9410230", "9410170"],
}

_last_call = 0.0
_pace = 0.35


def check_prefix(prefix: str) -> str:
    if not prefix.endswith("/"):
        prefix += "/"
    if not prefix.startswith("tide/") or ".." in prefix:
        raise SystemExit("prefix must be under tide/")
    if prefix == "tide/v1/" or prefix.startswith("tide/v1/"):
        raise SystemExit("refusing production prefix tide/v1/ (preview port only)")
    if not any(prefix.startswith(a) for a in ALLOWED):
        raise SystemExit(f"prefix {prefix!r} is not a preview tide prefix ({ALLOWED})")
    return prefix


def coops_prefix(chart_prefix: str) -> str:
    return check_prefix(chart_prefix) + "coops/"


def gmt(ms: int) -> str:
    return D.datetime.fromtimestamp(ms / 1000, D.timezone.utc).strftime("%Y%m%d %H:%M")


def fmt_t(ms: int) -> str:
    return D.datetime.fromtimestamp(ms / 1000, D.timezone.utc).strftime("%Y-%m-%d %H:%M")


def parse_t(s: str) -> int:
    s = urllib.parse.unquote(s)
    s = s.replace("%20", " ").replace("+", " ")
    if "T" in s:
        s = s.replace("T", " ")
    if re.match(r"^\d{8} ", s):
        return int(D.datetime.strptime(s, "%Y%m%d %H:%M").replace(tzinfo=D.timezone.utc).timestamp() * 1000)
    return int(D.datetime.strptime(s[:16], "%Y-%m-%d %H:%M").replace(tzinfo=D.timezone.utc).timestamp() * 1000)


def now_ms() -> int:
    return int(time.time() * 1000)


def archive_blackout(at: D.datetime | None = None) -> tuple[bool, str]:
    """True if an ingest must not start because a tide-archive slot may be running."""
    at = at or D.datetime.now(D.timezone.utc)
    # minutes since 00:00 UTC
    mins = at.hour * 60 + at.minute
    for h in ARCHIVE_HOURS:
        start = h * 60 + BLACKOUT_BEFORE_MIN
        end = h * 60 + BLACKOUT_AFTER_MIN
        # wrap past midnight (20:15 -> 22:20 is same day; no wrap needed)
        if start <= mins < end:
            return True, f"tide-archive blackout {h:02d}:15–{(h+2)%24:02d}:20 UTC (now {at:%H:%M} UTC)"
    return False, ""


def set_pace(sec: float) -> None:
    global _pace
    _pace = max(0.0, float(sec))


def _sleep_pace() -> None:
    global _last_call
    wait = _pace - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def http_get(url: str, tries: int = 5) -> bytes:
    err = None
    for i in range(tries):
        _sleep_pace()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            err = e
            code = getattr(e, "code", None) or getattr(getattr(e, "reason", None), "errno", None)
            if isinstance(e, urllib.error.HTTPError):
                code = e.code
            delay = (20, 45, 90, 90, 90)[min(i, 4)] if code in (403, 429) else (2 + 3 * i)
            time.sleep(delay)
    raise err


def product_file(root: str, st: str, product: str) -> str:
    return os.path.join(root, st, f"{product}.json")


def load_series(root: str, st: str, product: str) -> dict:
    fn = product_file(root, st, product)
    if not os.path.isfile(fn):
        return {"station": st, "product": product, "pts": [], "updated": None, "last_t": None, "calls": 0}
    j = json.load(open(fn))
    j.setdefault("pts", [])
    return j


def save_series(root: str, rec: dict) -> str:
    st, product = rec["station"], rec["product"]
    os.makedirs(os.path.join(root, st), exist_ok=True)
    fn = product_file(root, st, product)
    tmp = fn + ".tmp"
    json.dump(rec, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, fn)
    return fn


def merge_pts(old: list, new: list, keep_after: int) -> list:
    m = {t: v for t, v in old if t >= keep_after}
    for t, v in new:
        if t >= keep_after:
            m[t] = v
    return sorted(m.items())


def slice_pts(pts: list, b: int, e: int) -> list:
    return [[t, v] for t, v in pts if b <= t <= e]


def as_noaa(product: str, pts: list) -> dict:
    rows = [{"t": fmt_t(t), "v": (f"{v:.4f}" if isinstance(v, float) else str(v))} for t, v in pts]
    if product == "predictions":
        return {"predictions": rows}
    return {"data": rows}


def needed_window(product: str, now: int) -> tuple[int, int]:
    start = now - SLOW_DAYS * DAY - DAY
    if product == "predictions":
        return start, now + PRED_LEAD
    if product == "water_level":
        return start, now + WL_LEAD
    if product == "air_pressure":
        return start, now + AIR_LEAD
    return start, now


def gap_to_fetch(pts: list, want_b: int, want_e: int, product: str = "") -> tuple[int, int] | None:
    """Return a single [begin, end] to append/fill, or None if the store already covers the window.

    Even when the end is current we still re-fetch a short overlap so NOAA QC
    revisions (often 0.001 ft on water_level within a day) merge in. That stays
    one datagetter call because the overlap is far under 30 days.
    """
    if not pts:
        return want_b, want_e
    first, last = pts[0][0], pts[-1][0]
    overlap = OVERLAP_WL if product == "water_level" else OVERLAP
    # If the past is short, refill from want_b (rare; after a long outage).
    if first > want_b + 12 * HR:
        return want_b, max(want_e, last)
    # Predictions and pressure: skip when the end is already current.
    # water_level: always include the overlap so same-day QC edits merge (still 1 call).
    if product != "water_level" and last >= want_e - 10 * 60000:
        return None
    return max(want_b, last - overlap), want_e


def fetch_datagetter(product: str, st: str, b: int, e: int, extra: str = "") -> tuple[list, int]:
    """Fetch [b, e], splitting into 30-day chunks only when the window is that long. Returns (pts, n_calls)."""
    out, n = [], 0
    t = b
    while t < e:
        chunk_e = min(e, t + 30 * DAY)
        q = (
            f"{API}?product={product}&application=pnw_weather_tides&station={st}"
            f"&begin_date={urllib.parse.quote(gmt(t))}&end_date={urllib.parse.quote(gmt(chunk_e))}"
            f"&time_zone=gmt&format=json{extra}"
        )
        j = json.loads(http_get(q))
        n += 1
        for p in (j.get("predictions") or j.get("data") or []):
            try:
                out.append((parse_t(p["t"]), float(p["v"])))
            except (ValueError, TypeError, KeyError):
                pass
        t = chunk_e
        if t <= b:
            break
    out.sort()
    dedup = []
    for p in out:
        if not dedup or p[0] > dedup[-1][0]:
            dedup.append(p)
        else:
            dedup[-1] = p
    return dedup, n


def update_product(root: str, st: str, product: str, now: int, force_full: bool = False) -> dict:
    rec = load_series(root, st, product)
    want_b, want_e = needed_window(product, now)
    extra = ""
    if product == "predictions":
        extra = "&datum=MLLW&interval=6&units=english"
    elif product == "water_level":
        extra = "&datum=MLLW&units=english"
    elif product == "air_pressure":
        extra = "&units=metric&interval=h"
    # A station with no barometer (empty air_pressure) must not be re-pulled over 30 days every cycle.
    if (not force_full and not (rec.get("pts") or []) and rec.get("empty")
            and (rec.get("empty_until") or 0) > now):
        rec["calls"] = 0
        rec["fetched"] = None
        return rec
    window = None if force_full else gap_to_fetch(rec.get("pts") or [], want_b, want_e, product)
    if force_full:
        window = (want_b, want_e)
    calls = 0
    if window:
        pts, calls = fetch_datagetter(product, st, window[0], window[1], extra)
        rec["pts"] = merge_pts(rec.get("pts") or [], pts, now - KEEP_PAST)
        if not rec["pts"]:
            rec["empty"] = True
            rec["empty_until"] = now + DAY  # retry once a day, not every 6 min
        elif rec.get("empty"):
            rec["empty"] = False
            rec.pop("empty_until", None)
    rec["station"] = st
    rec["product"] = product
    rec["updated"] = D.datetime.now(D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["last_t"] = rec["pts"][-1][0] if rec["pts"] else None
    rec["first_t"] = rec["pts"][0][0] if rec["pts"] else None
    rec["n"] = len(rec["pts"])
    rec["calls"] = calls
    rec["fetched"] = [window[0], window[1]] if window else None
    save_series(root, rec)
    return rec


def load_meta(root: str, st: str, which: str) -> dict | None:
    fn = os.path.join(root, st, f"meta_{which}.json")
    if not os.path.isfile(fn):
        return None
    return json.load(open(fn))


def update_meta(root: str, st: str, now: int, max_age_ms: int = 24 * HR) -> int:
    """Refresh mdapi floodlevels + datums if missing or older than max_age_ms. Returns call count."""
    calls = 0
    os.makedirs(os.path.join(root, st), exist_ok=True)
    for which, path in (("floodlevels", f"{MD}{st}.json?expand=floodlevels"), ("datums", f"{MD}{st}/datums.json")):
        fn = os.path.join(root, st, f"meta_{which}.json")
        age_ok = False
        if os.path.isfile(fn):
            try:
                j = json.load(open(fn))
                fetched = j.get("_fetched_ms") or 0
                age_ok = now - fetched < max_age_ms
            except Exception:
                age_ok = False
        if age_ok:
            continue
        body = json.loads(http_get(path))
        body["_fetched_ms"] = now
        tmp = fn + ".tmp"
        json.dump(body, open(tmp, "w"), separators=(",", ":"))
        os.replace(tmp, fn)
        calls += 1
    return calls


def write_index(root: str, stats: dict) -> None:
    os.makedirs(root, exist_ok=True)
    fn = os.path.join(root, "index.json")
    json.dump(stats, open(fn, "w"), indent=1)


def fulfill_datagetter(root: str, url: str, now: int | None = None) -> tuple[int, str, bytes] | None:
    """Build a NOAA-shaped JSON body from the store for a datagetter URL. None if not a CO-OPS series URL."""
    if "tidesandcurrents.noaa.gov/api/prod/datagetter" not in url:
        return None
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    def one(k, default=None):
        v = q.get(k) or ([default] if default is not None else [])
        return v[0] if v else default
    product, st = one("product"), one("station")
    if not product or not st:
        return 400, "application/json", b'{"error":{"message":"missing product/station"}}'
    rec = load_series(root, st, product if product != "air_pressure" else "air_pressure")
    pts = rec.get("pts") or []
    if one("range"):
        # pressure() uses range=3 (metric, last 3 days). Serve from the hourly store.
        rng = int(float(one("range")))
        t1 = now or now_ms()
        t0 = t1 - rng * DAY
        body = as_noaa(product, slice_pts(pts, t0, t1))
        return 200, "application/json", json.dumps(body).encode()
    b, e = one("begin_date"), one("end_date")
    if not b or not e:
        return 400, "application/json", b'{"error":{"message":"missing begin/end"}}'
    body = as_noaa(product, slice_pts(pts, parse_t(b), parse_t(e)))
    return 200, "application/json", json.dumps(body).encode()


def fulfill_mdapi(root: str, url: str) -> tuple[int, str, bytes] | None:
    if "tidesandcurrents.noaa.gov/mdapi/" not in url:
        return None
    m = re.search(r"/stations/(\d{7})(?:/(datums))?\.json", url)
    if not m:
        return 404, "application/json", b"{}"
    st, datums = m.group(1), m.group(2)
    which = "datums" if datums else "floodlevels"
    j = load_meta(root, st, which)
    if not j:
        return 404, "application/json", b"{}"
    j = dict(j)
    j.pop("_fetched_ms", None)
    return 200, "application/json", json.dumps(j).encode()


def fulfill(root: str, url: str, now: int | None = None) -> tuple[int, str, bytes] | None:
    return fulfill_datagetter(root, url, now) or fulfill_mdapi(root, url)
