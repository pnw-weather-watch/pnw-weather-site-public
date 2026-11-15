#!/usr/bin/env python3
"""PNW Weather Tides page guard (port of Benjamin's tide_viewer_guard.py at 3e8607a, 2026-11-14; Studio checks removed).

Checks:
  1 map page has a visible Tides control that opens tide/
  2 tide/ (1440x900 @2x and 390x844 @3x phone): draws, no page/console errors, canvas backing = CSS size x DPR,
    official prediction + observed + Conditional Prediction present in the data AND painted, a "Now" line in range,
    no horizontal overflow on the phone
  3 station switch (Seattle) redraws and stays in the address; a reload keeps station + days; the California tab
    (state tab) opens San Francisco by default, writes state=ca, survives a reload, and switching back to Washington
    restores the last Washington station (per-tab memory)
  5 verification: the archive index loads from this repo's tide-archive branch (raw.githubusercontent.com, 200), the
    dashed "Conditional, verified" line has points AND is painted, the stats box has Conditional + Official MAE/bias over
    >= 24 hourly points and is drawn fully inside the chart, and calibration is NOT shown
  6 flood levels: live triple-check (tide_flood_verify.py) agrees with the FLOOD table in the served tide.js; on every
    station (both tabs) the drawn lines equal that table, nothing unverified is drawn, every level within 3 ft of the data
    is drawn, colors painted where all three are in range; label placement rules (far left, 0-3 px above the line,
    ~9.5 CSS px, full-width lines, knockouts, no overlap) at 1440x900, 1920x1080 and 390x844 for Westport, Seattle,
    Tacoma, Friday Harbor, Port Townsend, Cherry Point, Birch Bay, San Francisco, San Diego and La Jolla; no flood rows
    in the legend
  7 station lists: each tab A to Z by name, the dropdown matches the active tab's list, default Washington / Westport,
    Birch Bay present (alias of Cherry Point 9449424)
  8 hover readout (desktop pointer / phone tap): Pacific time, series + flood stages, crosshair, never over the plot, axis
    labels, legend, stats or notes, no layout shift; phone has the reserved 3-line slot
  9 Flood levels toggle: default ON, off hides lines/labels/readout rows, on restores, persists in localStorage tide:flood
 10 Wind surge chip (guide 15): default OFF, persisted in localStorage (tide:wind); the Conditional method is "stofs-free"
    (or "stofs-free+wind"); qa().windTest must report wind-on minus wind-off equals the wind component, zero-wind hours match.
If NOAA or GitHub raw is unreachable from this box the failure is recorded as an outage (block=False), never as a skip.
Usage: tide_viewer_guard.py <site url> [shotdir] [--json PATH]   Exit 0 = PASS, 1 = FAIL.
"""
import asyncio, json, os, sys, urllib.request
from pathlib import Path
_ARGV, JSON_OUT = list(sys.argv[1:]), None
if "--json" in _ARGV:
    _k = _ARGV.index("--json"); JSON_OUT = _ARGV[_k + 1] if _k + 1 < len(_ARGV) else None; del _ARGV[_k:_k + 2]
ARGS = [a for a in _ARGV if not a.startswith("--")]
B = ARGS[0].rstrip("/") if ARGS else ""
SHOT = ARGS[1] if len(ARGS) > 1 else None
class qa:   # local / preview build: no Access headers are needed or used by this guard
    @staticmethod
    async def add_hdr(route): await route.continue_()
    @staticmethod
    def headers(): return {}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tide_flood_verify as FV
from playwright.async_api import async_playwright

fails = []   # (msg, always_block)
def fail(msg, block=True): fails.append((msg, block)); print("FAIL", msg, flush=True)

def boxes_intersect(a, b, eps=0.5):
    if not a or not b: return False
    return (a["x"] + a["w"] > b["x"] + eps and b["x"] + b["w"] > a["x"] + eps and
            a["y"] + a["h"] > b["y"] + eps and b["y"] + b["h"] > a["y"] + eps)

def box_inside(inner, outer, eps=1.0):
    if not inner or not outer: return False
    return (inner["x"] >= outer["x"] - eps and inner["y"] >= outer["y"] - eps and
            inner["x"] + inner["w"] <= outer["x"] + outer["w"] + eps and
            inner["y"] + inner["h"] <= outer["y"] + outer["h"] + eps)

def layout_sig(lay):
    if not lay: return None
    return {k: lay.get(k) for k in ("X0", "X1", "Y0", "Y1", "slotH")}

def check_readout_clear(tag, hov, phone=False, layout0=None):
    """Readout must not cover the plot, axis labels, legend, verification box, or notes, and must not shift layout."""
    h = (hov or {}).get("h") or {}
    tip, plot = h.get("tip"), h.get("plot")
    regs = h.get("regions") or {}
    if not tip or not plot:
        fail(f"{tag}: hover readout missing tip/plot rects ({h})"); return
    names = (("plot", plot or regs.get("plot")), ("legend", regs.get("legend")),
             ("axis", regs.get("axis")), ("axisY", regs.get("axisY")),
             ("stats", regs.get("stats")), ("notes", regs.get("notes")))
    for name, box in names:
        if boxes_intersect(tip, box):
            fail(f"{tag}: hover readout intersects the {name} (tip={tip} {name}={box})")
    if phone:
        slot = regs.get("slot")
        if not slot: fail(f"{tag}: phone is missing the reserved readout slot")
        elif not box_inside(tip, slot):
            fail(f"{tag}: phone readout is not inside the reserved slot (tip={tip} slot={slot})")
    else:
        slot = regs.get("slot") or ((h.get("layout") or {}).get("slotH") or 0)
        if slot and (isinstance(slot, dict) or slot):
            if isinstance(slot, dict) or (isinstance(slot, (int, float)) and slot):
                if (h.get("layout") or {}).get("slotH"):
                    fail(f"{tag}: desktop unexpectedly has a phone readout slot ({h.get('layout')})")
    if layout0 is not None:
        lay1 = layout_sig(h.get("layout"))
        if layout_sig(layout0) != lay1:
            fail(f"{tag}: hover shifted the chart layout ({layout0} -> {lay1})")

ARCH_IDX = os.environ.get("TIDE_ARCH_IDX", "https://raw.githubusercontent.com/pnw-weather-watch/pnw-weather-site-public/tide-archive/v1/index.json")
def arch_up():
    try: return b'"months"' in urllib.request.urlopen(ARCH_IDX, timeout=30).read()
    except Exception: return False

def noaa_up():
    try:
        u = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=pnw_weather_tide_guard&station=9441102"
             "&date=today&datum=MLLW&time_zone=gmt&units=english&interval=hilo&format=json")
        return b"predictions" in urllib.request.urlopen(u, timeout=30).read()
    except Exception:
        return False

# pixel counts of the three line colors (pred #5aa9ff, obs #ff5d5d, cond #ffb02e) on a canvas
COLORS = """(id) => { const c = document.getElementById(id); if (!c || !c.width) return null; const g = c.getContext('2d');
  const d = g.getImageData(0, 0, c.width, c.height).data; const n = {pred: 0, obs: 0, cond: 0, ver: 0};
  const near = (i, r, gg, b) => Math.abs(d[i]-r) < 40 && Math.abs(d[i+1]-gg) < 40 && Math.abs(d[i+2]-b) < 40;
  for (let i = 0; i < d.length; i += 16) { if (near(i, 0x5a, 0xa9, 0xff)) n.pred++; else if (near(i, 0xff, 0x5d, 0x5d)) n.obs++; else if (near(i, 0xff, 0xb0, 0x2e)) n.cond++; else if (near(i, 0xdc, 0xc0, 0x8c)) n.ver++; }
  return n; }"""
# flood line colors (minor #ff7a45, moderate #e6194b, major #c74bff), tight tolerance: minor is close to the observed red
FCOLORS = """(id) => { const c = document.getElementById(id); if (!c || !c.width) return null; const g = c.getContext('2d');
  const d = g.getImageData(0, 0, c.width, c.height).data; const n = {minor: 0, moderate: 0, major: 0};
  const near = (i, r, gg, b) => Math.abs(d[i]-r) < 14 && Math.abs(d[i+1]-gg) < 14 && Math.abs(d[i+2]-b) < 14;
  for (let i = 0; i < d.length; i += 4) { if (near(i, 0xff, 0x7a, 0x45)) n.minor++; else if (near(i, 0xe6, 0x19, 0x4b)) n.moderate++; else if (near(i, 0xc7, 0x4b, 0xff)) n.major++; }
  return n; }"""
FLV = ("minor", "moderate", "major")

def flood_triple_check():
    """Live triple-check against the FLOOD table in the SERVED tide.js. Returns (table, alias) or (None, None)."""
    import tempfile
    try: src = urllib.request.urlopen(urllib.request.Request(B + "/tide/tide.js", headers={**(qa.headers() if hasattr(qa, "headers") else {}), "User-Agent": "Mozilla/5.0 pnw_weather_tide_guard"}), timeout=60).read().decode()
    except Exception as e: fail(f"flood: could not read {B}/tide/tide.js ({e})"); return None, None
    tf = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False); tf.write(src); tf.close()
    st, alias, table = FV.stations_from_tidejs(tf.name)
    if not table: fail("flood: served tide.js has no verified FLOOD table"); return None, None
    try: rows = FV.check(sorted({alias.get(k, k) for k, _ in st}))
    except Exception as e: fail(f"flood: triple-check sources unreachable ({type(e).__name__}: {str(e)[:150]})", block=False); return table, alias
    for sid, r in rows.items():
        for k in FLV:
            x = r["levels"][k]; have = (table.get(sid) or {}).get(k)
            if x["status"] == "MISMATCH" and have is not None: fail(f"flood: {sid} {k} sources disagree on a drawn level S1={x['s1_nws']} S2={x['s2']} S3={x['s3']}")
            if (x["draw"] is None) != (have is None) or (have is not None and abs(x["draw"] - have) > FV.TOL):
                fail(f"flood: {sid} {k} tide.js table {have} but the live triple-check says {x['draw']} ({x['status']})")
        print(f"  flood {sid} {r['name']}: " + ", ".join(f"{k}={r['levels'][k]['draw']} [{r['levels'][k]['status']}]" for k in FLV) + f" | {r['s3note']}")
    return table, alias

FLABEL_ORDER = ("minor", "moderate", "major")

def check_flood_labels(tag, q, phone=False):
    """Full-width flood lines with far-left names; knockouts only where a line would run through a word."""
    labs = q.get("floodLabels") or []
    exp = sorted(q.get("floodDrawn") or [])
    if sorted(l["k"] for l in labs) != exp:
        fail(f"flood: {tag} labels {[l['k'] for l in labs]} != lines {exp}")
        return
    if not labs:
        return
    s = labs[0].get("s") or 1
    plotX0 = labs[0].get("plotX0", 0)
    plotX1 = labs[0].get("plotX1")
    plotW = (plotX1 - plotX0) if plotX1 is not None else None
    for l in labs:
        if "y1" not in l or "ly" not in l:
            fail(f"flood: {tag} {l.get('k')} label missing y1/ly ({l})"); continue
        gap = l["ly"] - l["y1"]
        if gap < -0.05 or gap > 3.05:
            fail(f"flood: {tag} {l['k']} label bottom is {gap:.1f}px from its line (want 0-3 px above)")
        css = l.get("fontCss")
        if css is None:
            fail(f"flood: {tag} {l['k']} missing fontCss")
        elif css < 8.95:
            fail(f"flood: {tag} {l['k']} fontCss {css} is below 9px")
        elif (not phone) and s <= 1.35 and not (9.0 <= css <= 10.5):
            fail(f"flood: {tag} {l['k']} fontCss {css} is not ~9.5px on desktop")
        lx0 = l.get("lineX0", plotX0)
        lx1 = l.get("lineX1", plotX1 if plotX1 is not None else lx0)
        if plotW and plotW > 0:
            if lx0 > plotX0 + 2 or lx1 < plotX1 - 2:
                fail(f"flood: {tag} {l['k']} line does not start/end at the plot edge (line {lx0:.1f}-{lx1:.1f}, plot {plotX0:.1f}-{plotX1:.1f})")
            span = (lx1 - lx0) / plotW
            if span < 0.95:
                fail(f"flood: {tag} {l['k']} line spans {100*span:.1f}% of the plot (need >= 95%)")
        byk = {x["k"]: x for x in labs}
        for ko in (l.get("knockouts") or []):
            src = byk.get(ko.get("k"))
            width = ko["x1"] - ko["x0"]
            maxw = ((src["x1"] - src["x0"]) + 6) if src else 6
            if width > maxw + 0.55:
                fail(f"flood: {tag} {l['k']} knockout for {ko.get('k')} is {width:.1f}px wide (max {maxw:.1f})")
    # far left: every non-offset word; offset is allowed only when noted
    for l in labs:
        pad = l["x0"] - plotX0
        if l.get("offset"):
            if not (q.get("floodLabelNote") or ""):
                fail(f"flood: {tag} {l['k']} is offset but no floodLabelNote was set")
            if plotW and l["x1"] > plotX0 + 0.5 * plotW:
                fail(f"flood: {tag} offset {l['k']} is not on the left side of the plot")
        elif pad < 3 * s or pad > 10 * s:
            fail(f"flood: {tag} {l['k']} is not at the far left (x0-plotX0={pad:.1f}, s={s})")
    nc = q.get("nowChip")   # PNW Weather: the "Now" chip must never cover a flood word
    if nc:
        for l in labs:
            if l["x0"] < nc["x"] + nc["w"] and nc["x"] < l["x1"] and l["y0"] < nc["y"] + nc["h"] and nc["y"] < l["y1"]:
                fail(f"flood: {tag} the Now chip covers the {l['k']} label (chip={nc})")
    if q.get("floodLabelNote"):
        print(f"  note {tag}: {q.get('floodLabelNote')}")
    for i, a_ in enumerate(labs):
        for b_ in labs[i + 1:]:
            if a_["x0"] < b_["x1"] and b_["x0"] < a_["x1"] and a_["y0"] < b_["y1"] and b_["y0"] < a_["y1"]:
                fail(f"flood: {tag} labels {a_['k']}/{b_['k']} overlap")
    # a line may not run through another word unless that x-range is knocked out
    for l in labs:
        for o in labs:
            if o["k"] == l["k"]:
                continue
            half = (o.get("lineW") or 2) / 2
            if not (l["y0"] < o["ly"] + half + 0.5 and l["y1"] > o["ly"] - half - 0.5):
                continue
            covered = False
            for ko in (o.get("knockouts") or []):
                if ko["x0"] <= l["x0"] + 0.5 and ko["x1"] >= l["x1"] - 0.5:
                    covered = True; break
            if not covered:
                fail(f"flood: {tag} {o['k']} line passes through {l['k']} label without a knockout")

def _regression_must_fail(name, q, expect_sub):
    n0 = len(fails)
    check_flood_labels(name, q)
    new_fails = fails[n0:]
    del fails[n0:]
    text = "; ".join(m for m, _ in new_fails)
    if not new_fails or not any(s in text for s in expect_sub):
        fail(f"flood: guard would still pass {name} (got: {text or 'no fails'})")
    else:
        print(f"  regression: {name} correctly FAILs: {text}")

def old_layout_regressions():
    """623f9aa truncated lines, and the earlier stacked crop with a line through Moderate, must both fail."""
    # 623f9aa Westport 1920x1080: lines started at the word, so Major/Moderate did not span the hindcast.
    trunc = [
        {"k": "minor", "x0": 82.5, "x1": 113.5, "y0": 225.96, "y1": 237.46, "ly": 239.46, "plotX0": 75, "plotX1": 1876.5, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 82.5, "lineX1": 1876.5, "offset": False, "knockouts": []},
        {"k": "moderate", "x0": 121.5, "x1": 171.5, "y0": 206.56, "y1": 218.06, "ly": 220.06, "plotX0": 75, "plotX1": 1876.5, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 121.5, "lineX1": 1876.5, "offset": False, "knockouts": []},
        {"k": "major", "x0": 179.5, "x1": 209.5, "y0": 187.15, "y1": 198.65, "ly": 200.65, "plotX0": 75, "plotX1": 1876.5, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 179.5, "lineX1": 1876.5, "offset": False, "knockouts": []},
    ]
    _regression_must_fail("regression-623f9aa-truncated-lines",
                          {"floodLabels": trunc, "floodDrawn": ["major", "minor", "moderate"]},
                          ["does not start/end at the plot edge", "spans "])
    # Earlier stacked layout: full-width lines, Major line through Moderate, no knockout.
    stacked = [
        {"k": "minor", "x0": 82.5, "x1": 118.5, "y0": 226.46, "y1": 237.46, "ly": 239.46, "plotX0": 75, "plotX1": 1400, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 75, "lineX1": 1400, "offset": False, "knockouts": []},
        {"k": "moderate", "x0": 82.5, "x1": 142.5, "y0": 198.0, "y1": 218.06, "ly": 220.06, "plotX0": 75, "plotX1": 1400, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 75, "lineX1": 1400, "offset": False, "knockouts": []},
        {"k": "major", "x0": 82.5, "x1": 117.5, "y0": 185.65, "y1": 198.65, "ly": 200.65, "plotX0": 75, "plotX1": 1400, "fontCss": 9.5, "lineW": 2.5, "s": 1.25, "lineX0": 75, "lineX1": 1400, "offset": False, "knockouts": []},
    ]
    _regression_must_fail("regression-stacked-line-through-word",
                          {"floodLabels": stacked, "floodDrawn": ["major", "minor", "moderate"]},
                          ["passes through", "overlap"])

PIXEL_OTHER_LINE = """() => {
  const q = window.TIDE.qa(), labs = q.floodLabels || [];
  const c = document.getElementById('tc'); if (!c) return {err: 'no canvas'};
  const g = c.getContext('2d');
  const dpr = (window.__tideSharp && window.__tideSharp.dpr) || 1;
  const cols = {minor:[255,122,69], moderate:[230,25,75], major:[199,75,255]};
  const near = (p, t) => Math.abs(p[0]-t[0])<18 && Math.abs(p[1]-t[1])<18 && Math.abs(p[2]-t[2])<18;
  const hits = [];
  for (const l of labs) {
    const x0 = Math.max(0, Math.floor(l.x0 * dpr) + 1), x1 = Math.min(c.width, Math.ceil(l.x1 * dpr) - 1);
    const y0 = Math.max(0, Math.floor(l.y0 * dpr) + 1), y1 = Math.min(c.height, Math.ceil(l.y1 * dpr) - 1);
    if (x1 <= x0 || y1 <= y0) continue;
    const d = g.getImageData(x0, y0, x1 - x0, y1 - y0).data;
    const count = {minor:0, moderate:0, major:0};
    for (let i = 0; i < d.length; i += 4) {
      for (const k of Object.keys(cols)) if (k !== l.k && near([d[i], d[i+1], d[i+2]], cols[k])) count[k]++;
    }
    const bad = Object.entries(count).filter(([, n]) => n > 8);
    if (bad.length) hits.push({k: l.k, bad});
  }
  return {hits};
}"""

async def check_label_pixels(pg, tag):
    hit = await pg.evaluate(PIXEL_OTHER_LINE)
    if hit.get("err"):
        fail(f"flood: {tag} pixel check {hit['err']}")
    elif hit.get("hits"):
        fail(f"flood: {tag} visible other-line pixels inside label(s) {hit['hits']}")

async def label_viewports_check(br):
    """Extra sizes for the close-level stations (1440x900 is already covered in stations_check)."""
    sts = [("9441102", "Westport"), ("9447130", "Seattle"), ("9446484", "Tacoma"), ("9449880", "Friday Harbor"),
           ("9444900", "Port Townsend"), ("9449424", "Cherry Point"), ("birchbay", "Birch Bay"),
           ("9414290", "San Francisco"), ("9410170", "San Diego"), ("9410230", "La Jolla")]
    views = [(1920, 1080, 2, False, "1920x1080"), (390, 844, 3, True, "phone390")]
    for W, H, dpr, phone, vtag in views:
        ctx = await br.new_context(viewport={"width": W, "height": H}, device_scale_factor=dpr, is_mobile=phone, has_touch=phone)
        await ctx.route(B + "/**", qa.add_hdr)
        pg = await ctx.new_page()
        for key, nm in sts:
            tag = f"{nm} {vtag}"
            await pg.goto(f"{B}/tide/?st={key}&days=9", wait_until="load", timeout=90000)
            try:
                await pg.wait_for_function("(k) => window.__tideDrawn > 0 && window.TIDE.qa().st === k", arg=key, timeout=90000)
            except Exception as e:
                fail(f"flood: {tag} did not load ({e})", block=not DATA_DOWN); continue
            await pg.wait_for_timeout(250)
            q = await pg.evaluate("() => window.TIDE.qa()")
            check_flood_labels(tag, q, phone=phone)
            await check_label_pixels(pg, tag)
            print(f"  labels {tag}: fontCss={(q.get('floodLabels') or [{}])[0].get('fontCss')} offset={[l['k'] for l in (q.get('floodLabels') or []) if l.get('offset')]} note={q.get('floodLabelNote')} labels={[l['k'] for l in (q.get('floodLabels') or [])]}")
        await ctx.close()

async def stations_check(br, table, alias):
    ctx = await br.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1); await ctx.route(B + "/**", qa.add_hdr)
    pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror " + str(e)[:200]))
    pg.on("console", lambda m: m.type == "error" and errs.append("console " + m.text[:200]))
    await pg.goto(B + "/tide/", wait_until="load", timeout=90000)
    try: await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
    except Exception as e: fail(f"stations: tide page never loaded ({e})"); await ctx.close(); return
    sts = await pg.evaluate("() => window.TIDE.stations")
    states = await pg.evaluate("() => Object.fromEntries(Object.entries(window.TIDE.states).map(([k, v]) => [k, {d: v.defaultSt, s: v.stations}]))")
    if sorted(states) != ["ca", "wa"]: fail(f"stations: state tabs are {sorted(states)} (want wa, ca)")
    if (await pg.evaluate("() => window.TIDE.tab()")) != "wa": fail("stations: default tab is not Washington")
    if (await pg.evaluate("() => window.TIDE.qa().st")) != "9441102": fail("stations: default station is not Westport 9441102")
    for sk, sv in states.items():
        names = [n for _, n in sv["s"]]
        if names != sorted(names, key=str.casefold): fail(f"stations: {sk} list is not A to Z: {names}")
        print(f"  stations {sk} A-Z ({len(names)}): {names}")
    if not any(n.startswith("Birch Bay") for _, n in states.get("wa", {}).get("s", [])): fail("stations: Birch Bay missing from Washington")
    if any("Sacramento" in n for _, n in states.get("ca", {}).get("s", [])): fail("stations: West Sacramento must be omitted")
    if states.get("ca", {}).get("d") != "9414290": fail(f"stations: California default is {states.get('ca', {}).get('d')} (want San Francisco 9414290)")
    for sk in ("wa", "ca"):
        await pg.click(f"#stab button[data-state={sk}]"); await pg.wait_for_timeout(200)
        opts = await pg.evaluate("() => [...document.getElementById('st').options].map(o => o.value)")
        if opts != [k for k, _ in states[sk]["s"]]: fail(f"stations: {sk} dropdown {opts} != TIDE.states.{sk}")
    for key, nm in sts:
        await pg.goto(f"{B}/tide/?st={key}&days=9", wait_until="load", timeout=90000)
        try: await pg.wait_for_function("(k) => window.__tideDrawn > 0 && window.TIDE.qa().st === k", arg=key, timeout=90000)
        except Exception as e: fail(f"stations: {nm} did not load ({e})", block=not DATA_DOWN); continue
        await pg.wait_for_timeout(300)
        q = await pg.evaluate("""() => { const q = window.TIDE.qa(), D = window.TIDE.state(); let hi = -1e9;
          for (const a of [D.pred, D.obs, D.cond, D.ver]) for (const p of a) hi = Math.max(hi, p[1]); q.dataHi = hi; return q; }""")
        sid = q.get("sid"); want = (table or {}).get(alias.get(key, key)) or {}
        tab = await pg.evaluate("() => window.TIDE.tab()")
        if key not in [k for k, _ in states[tab]["s"]]: fail(f"stations: {nm} opened on the {tab} tab, which does not list it")
        if key == "birchbay" or nm.startswith("Birch Bay"):
            if sid != "9449424": fail(f"stations: Birch Bay data station is {sid} (expected Cherry Point 9449424)")
            for k in ("pred", "obs", "cond"):
                if not q.get(k): fail(f"stations: Birch Bay has no {k} points", block=not DATA_DOWN)
        got = {f["k"]: f["v"] for f in q.get("floods") or []}
        if table is not None:
            for k in FLV:
                if (k in got) != (k in want) or (k in got and abs(got[k] - want[k]) > FV.TOL):
                    fail(f"flood: {nm} {k} drawn value {got.get(k)} != verified {want.get(k)} (skip={q.get('floodSkip')})", block=not DATA_DOWN)
            extra = [k for k in got if k not in want]
            if extra: fail(f"flood: {nm} draws unverified levels {extra}")
        exp = sorted(k for k, v in got.items() if v < q["dataHi"] + 3)
        if sorted(q.get("floodDrawn") or []) != exp: fail(f"flood: {nm} lines drawn {q.get('floodDrawn')} but in range {exp}")
        # t3052u: full-width lines, far-left names, knockouts, no line pixels in a word
        check_flood_labels(nm, q, phone=False)
        await check_label_pixels(pg, nm)
        leg = q.get("legend") or []
        if any("flood" in (x or "").lower() for x in leg): fail(f"flood: {nm} legend still has flood rows {leg}")
        if not any("Official prediction" in (x or "") for x in leg): fail(f"flood: {nm} legend missing Official prediction ({leg})")
        if q.get("floodLabelNote"): print(f"  note {nm}: {q.get('floodLabelNote')}")
        if all(k in exp for k in FLV):
            n = await pg.evaluate(FCOLORS, "tc")
            if not n or min(n.values()) < 40: fail(f"flood: {nm} minor/moderate/major colors not painted {n}")
            else: print(f"  flood {nm}: painted px {n}")
        print(f"  {nm} ({key} -> {sid}): floods={got} drawn={q.get('floodDrawn')} dataHi={q['dataHi']:.2f} method={q.get('method')}")
    real = [e for e in errs if "favicon" not in e]
    if real: fail(f"stations: console/page errors: {real[:4]}", block=not DATA_DOWN)
    await ctx.close()

BOX = "()=>['cv','ch'].map(i=>{const c=document.getElementById(i),b=c.getBoundingClientRect();return [b.left+scrollX,b.top+scrollY,b.width,b.height,c.width,c.height]})"

def check_qa(tag, q, want_st=None):
    if not q or q.get("err"): fail(f"{tag}: tide data did not load ({(q or {}).get('err')})", block=not DATA_DOWN); return False
    if want_st and q.get("st") != want_st: fail(f"{tag}: station {q.get('st')} (expected {want_st})")
    for k in ("pred", "obs", "cond"):
        if not q.get(k): fail(f"{tag}: no {k} points ({q.get(k)})")
    if q.get("method") not in ("stofs-free", "stofs-free+wind"): fail(f"{tag}: conditional method {q.get('method')!r} (want the STOFS-free default, guide 15)")
    wt = q.get("windTest")
    if wt is None or not wt.get("ok"):
        fail(f"{tag}: wind-on minus wind-off is not exactly the wind component ({wt})")
    sst_ = q.get("sst") or {}
    if sst_.get("src") in (None, "none"): print(f"  note {tag}: no SST sidecar row, warm-water term W=0 (fallback)")
    aifs_ = q.get("aifs") or {}
    if not str(aifs_.get("src") or "").startswith("aifs-ens"): print(f"  note {tag}: forecast pressure source {aifs_.get('src')!r} (AIFS ENS sidecar not used)")
    if q.get("method") == "persist": print(f"  note {tag}: STOFS guidance unavailable, persistence fallback used (not blocking)")
    if not (q.get("start", 0) <= q.get("now", 0) <= q.get("end", 0)): fail(f"{tag}: now line outside the default range")
    # verification (t3018u)
    if not q.get("issues"): fail(f"{tag}: no archived Conditional snapshots loaded from the tide-archive branch ({q.get('arch')})", block=not ARCH_DOWN)
    elif (q.get("ver") or 0) < 50: fail(f"{tag}: verified line has {q.get('ver')} points")
    st_ = q.get("stats") or {}
    if q.get("issues") and not (st_.get("n", 0) >= 24 and all(isinstance((st_.get(k) or {}).get(m), (int, float)) for k in ("cond", "off") for m in ("mae", "bias"))):
        fail(f"{tag}: stats box data missing or too few points ({ {k: st_.get(k) for k in ('n', 'cond', 'off')} })")
    if q.get("calib") is not None or st_.get("raw") is not None: fail(f"{tag}: calibration is shown on the chart/stats (must stay background-only)")
    sb = q.get("statsBox")
    if q.get("issues") and (not sb or sb["x"] < 0 or sb["y"] < 0 or sb["x"] + sb["w"] > sb["W"] + 0.5 or sb["y"] + sb["h"] > sb["H"] + 0.5):
        fail(f"{tag}: stats box not drawn inside the chart ({sb})")
    if "raw.githubusercontent.com/pnw-weather-watch/pnw-weather-site-public/tide-archive/" not in (q.get("arch") or ""): fail(f"{tag}: archive URL is {q.get('arch')!r}")
    print(f"  {tag}: archive issues={q.get('issues')} archived_live={q.get('archived')} ver={q.get('ver')} stats n={st_.get('n')} cond={st_.get('cond')} off={st_.get('off')}")
    print(f"  {tag}: st={q.get('st')} pred={q.get('pred')} obs={q.get('obs')} cond={q.get('cond')} method={q.get('method')} cycle={q.get('cycle')} rNow={q.get('rNow')} rSlow={q.get('rSlow')}")
    return True

async def tide_page(br, W, H, dpr, phone, tag):
    ctx = await br.new_context(viewport={"width": W, "height": H}, device_scale_factor=dpr, is_mobile=phone, has_touch=phone)
    await ctx.route(B + "/**", qa.add_hdr)
    pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror " + str(e)[:200]))
    pg.on("console", lambda m: m.type == "error" and errs.append("console " + m.text[:200]))
    arch_hits = []
    pg.on("response", lambda r: r.url.startswith(ARCH_IDX) and r.status == 200 and arch_hits.append(r.url))
    await pg.goto(B + "/tide/?st=9441102", wait_until="load", timeout=90000)
    try: await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
    except Exception as e: fail(f"{tag}: tide page never finished loading ({e})"); await ctx.close(); return
    await pg.wait_for_timeout(800)
    q = await pg.evaluate("() => window.TIDE && window.TIDE.qa()")
    ok = check_qa(tag, q, "9441102")
    sh = (q or {}).get("sharp") or {}
    if ok and (not sh or abs(sh.get("backingW", 0) - round(sh.get("cssW", 0) * min(dpr, 3))) > 2):
        fail(f"{tag}: chart canvas backing {sh.get('backingW')} != CSS {sh.get('cssW')} x DPR {dpr} (soft text)")
    if ok:
        n = await pg.evaluate(COLORS, "tc")
        if not n or n["pred"] < 50 or n["obs"] < 30 or n["cond"] < 50: fail(f"{tag}: line colors not painted {n}")
        else: print(f"  {tag}: painted px pred={n['pred']} obs={n['obs']} cond={n['cond']} ver={n['ver']}")
        if n and q.get("issues") and n["ver"] < 10: fail(f"{tag}: verified dashed line not painted {n}")
        if not arch_hits: fail(f"{tag}: the page did not fetch the archive index from GitHub with 200", block=not ARCH_DOWN)
        # t3052u: hover / tap readout + crosshair, flood stages in the tooltip, no flood rows in the legend
        leg = (q or {}).get("legend") or []
        if any("flood" in (x or "").lower() for x in leg): fail(f"{tag}: legend still has flood rows {leg}")
        pre = await pg.evaluate("() => { const g = window.TIDE.geom(), q = window.TIDE.qa(), ch = (q && q.chrome) || (g || {}); const r = document.getElementById('tc').getBoundingClientRect(); return { x: r.left + r.width * 0.55, y: r.top + (g ? (g.Y0 + g.Y1) / 2 : r.height * 0.42), layout: g && g.layout, slot: ch.slot || (g && g.slot), labels: (q.floodLabels || []).map(l => ({k:l.k,x0:l.x0,y0:l.y0,ly:l.ly})) }; }")
        if phone and not (pre.get("slot") or (pre.get("layout") or {}).get("slotH")):
            fail(f"{tag}: phone has no reserved readout slot before hover ({pre.get('layout')})")
        if (not phone) and (pre.get("layout") or {}).get("slotH"):
            fail(f"{tag}: desktop unexpectedly reserved a phone readout slot ({pre.get('layout')})")
        box = pre
        if not phone:
            await pg.mouse.move(box["x"], box["y"]); await pg.wait_for_timeout(250)
        else:
            await pg.touchscreen.tap(box["x"], box["y"]); await pg.wait_for_timeout(350)
        hov = await pg.evaluate("() => { const tip = document.getElementById('tip'); return { hidden: !tip || tip.hidden, text: tip ? tip.innerText : '', html: tip ? tip.innerHTML : '', h: window.__tideHover }; }")
        txt = (hov.get("text") or "") + " " + (hov.get("html") or "")
        if hov.get("hidden") or not (hov.get("h") or {}).get("t"): fail(f"{tag}: hover/tap readout did not appear ({ {k: hov.get(k) for k in ('hidden','text','h')} })")
        else:
            if not any(z in txt for z in ("PT", "PST", "PDT")): fail(f"{tag}: hover readout missing Pacific time ({hov.get('text')!r})")
            for need in ("Official prediction", "Minor flood"):
                if need.lower() not in txt.lower(): fail(f"{tag}: hover readout missing {need!r} ({hov.get('text')!r})")
            hx, y0, y1 = hov["h"].get("x"), hov["h"].get("y0"), hov["h"].get("y1")
            if hx is None or y0 is None or y1 is None or y1 <= y0: fail(f"{tag}: hover crosshair geometry missing ({hov.get('h')})")
            check_readout_clear(tag, hov, phone=phone, layout0=pre.get("layout"))
            post_labs = await pg.evaluate("() => (window.TIDE.qa().floodLabels || []).map(l => ({k:l.k,x0:l.x0,y0:l.y0,ly:l.ly}))")
            if pre.get("labels") and post_labs != pre.get("labels"):
                fail(f"{tag}: hover shifted flood label positions")
            print(f"  {tag}: hover readout ok t={hov['h'].get('t')} rows={len(hov['h'].get('rows') or [])} tip={hov['h'].get('tip')}")
        # t3060u: Flood levels chip default ON, off hides lines+labels+readout rows, on restores, persists
        tog = await pg.evaluate("() => { const b = document.getElementById('floodtog'); const q = window.TIDE.qa(); return { exists: !!b, pressed: b && b.getAttribute('aria-pressed'), text: b && b.textContent, floodOn: q.floodOn, drawn: q.floodDrawn, nlab: (q.floodLabels || []).length }; }")
        if not tog or not tog.get("exists") or "Flood levels" not in (tog.get("text") or ""):
            fail(f"{tag}: Flood levels toggle chip missing ({tog})")
        elif tog.get("pressed") != "true" or not tog.get("floodOn") or not tog.get("drawn"):
            fail(f"{tag}: Flood levels toggle is not on by default ({tog})")
        n0 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#floodtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n", arg=n0, timeout=10000)
        except Exception as e: fail(f"{tag}: Flood levels off did not redraw ({e})")
        await pg.wait_for_timeout(150)
        qoff = await pg.evaluate("() => { const q = window.TIDE.qa(), b = document.getElementById('floodtog'); return { floodOn: q.floodOn, drawn: q.floodDrawn, labels: q.floodLabels, pressed: b && b.getAttribute('aria-pressed'), ls: localStorage.getItem('tide:flood') }; }")
        if qoff.get("floodOn") or qoff.get("drawn") or qoff.get("labels") or qoff.get("pressed") != "false":
            fail(f"{tag}: Flood levels off still shows lines/labels ({qoff})")
        if qoff.get("ls") != "0": fail(f"{tag}: Flood levels off did not persist to localStorage ({qoff.get('ls')!r})")
        # re-hover / re-tap and confirm flood rows are gone, readout still outside the plot
        if not phone:
            await pg.mouse.move(box["x"], box["y"]); await pg.wait_for_timeout(250)
        else:
            await pg.touchscreen.tap(box["x"], box["y"]); await pg.wait_for_timeout(350)
        hoff = await pg.evaluate("() => { const tip = document.getElementById('tip'); return { hidden: !tip || tip.hidden, text: tip ? tip.innerText : '', h: window.__tideHover }; }")
        if hoff.get("hidden") or not (hoff.get("h") or {}).get("t"):
            fail(f"{tag}: hover/tap readout missing after Flood levels off ({hoff})")
        else:
            labs = " ".join(r.get("lab", "") for r in ((hoff.get("h") or {}).get("rows") or []))
            if "flood" in labs.lower() or "Minor flood" in (hoff.get("text") or ""):
                fail(f"{tag}: flood rows still in the readout after Flood levels off ({labs!r} text={hoff.get('text')!r})")
            check_readout_clear(f"{tag} flood-off", hoff, phone=phone)
        n1 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#floodtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n", arg=n1, timeout=10000)
        except Exception as e: fail(f"{tag}: Flood levels on did not redraw ({e})")
        qon = await pg.evaluate("() => { const q = window.TIDE.qa(), b = document.getElementById('floodtog'); return { floodOn: q.floodOn, drawn: q.floodDrawn, labels: q.floodLabels, pressed: b && b.getAttribute('aria-pressed'), ls: localStorage.getItem('tide:flood') }; }")
        if not qon.get("floodOn") or not qon.get("drawn") or not qon.get("labels") or qon.get("pressed") != "true":
            fail(f"{tag}: Flood levels on did not restore lines/labels ({ {k: qon.get(k) for k in ('floodOn','drawn','pressed','ls')} })")
        check_flood_labels(f"{tag} flood-on", {"floodLabels": qon.get("labels"), "floodDrawn": qon.get("drawn"), "floodLabelNote": (await pg.evaluate('() => window.TIDE.qa().floodLabelNote'))}, phone=phone)
        # persist across reload
        n2 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#floodtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n", arg=n2, timeout=10000)
        except Exception as e: fail(f"{tag}: Flood levels off (persist) did not redraw ({e})")
        await pg.reload(wait_until="load")
        try:
            await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
            qls = await pg.evaluate("() => { const q = window.TIDE.qa(), b = document.getElementById('floodtog'); return { st: q.st, floodOn: q.floodOn, drawn: q.floodDrawn, labels: q.floodLabels, pressed: b && b.getAttribute('aria-pressed'), ls: localStorage.getItem('tide:flood') }; }")
            if qls.get("floodOn") or qls.get("drawn") or qls.get("labels") or qls.get("pressed") != "false" or qls.get("ls") != "0":
                fail(f"{tag}: Flood levels off did not survive reload ({qls})")
            else:
                print(f"  {tag}: Flood levels toggle off/on/persist ok")
        except Exception as e:
            fail(f"{tag}: reload after Flood levels off failed ({e})")
        # restore ON so later steps in this page (desk station switch) start from the default
        if await pg.evaluate("() => window.TIDE.qa().floodOn") is False:
            n3 = await pg.evaluate("() => window.__tideDrawn")
            await pg.click("#floodtog")
            try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().floodOn", arg=n3, timeout=10000)
            except Exception as e: fail(f"{tag}: could not restore Flood levels on ({e})")
        # Wind surge chip: default OFF, adds only wind, persists, identity holds
        wtog = await pg.evaluate("() => { const b = document.getElementById('windtog'); const q = window.TIDE.qa(); return { exists: !!b, pressed: b && b.getAttribute('aria-pressed'), text: b && b.textContent, windOn: q.windOn, method: q.method, windTest: q.windTest }; }")
        if not wtog or not wtog.get("exists") or "Wind surge" not in (wtog.get("text") or ""):
            fail(f"{tag}: Wind surge toggle chip missing ({wtog})")
        elif wtog.get("pressed") != "false" or wtog.get("windOn"):
            fail(f"{tag}: Wind surge toggle is not off by default ({wtog})")
        elif wtog.get("windTest") is not None and not (wtog.get("windTest") or {}).get("ok"):
            fail(f"{tag}: wind identity failed on default load ({wtog.get('windTest')})")
        nW = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#windtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().windOn === true", arg=nW, timeout=10000)
        except Exception as e: fail(f"{tag}: Wind surge on did not redraw ({e})")
        qwon = await pg.evaluate("() => { const q = window.TIDE.qa(), b = document.getElementById('windtog'); return { windOn: q.windOn, method: q.method, pressed: b && b.getAttribute('aria-pressed'), ls: localStorage.getItem('tide:wind'), windTest: q.windTest, cond: q.cond }; }")
        if not qwon.get("windOn") or qwon.get("pressed") != "true" or qwon.get("ls") != "1" or not qwon.get("cond"):
            fail(f"{tag}: Wind surge on did not stick ({qwon})")
        if qwon.get("windTest") is not None and not (qwon.get("windTest") or {}).get("ok"):
            fail(f"{tag}: wind identity failed with wind on ({qwon.get('windTest')})")
        nW2 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#windtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().windOn === false", arg=nW2, timeout=10000)
        except Exception as e: fail(f"{tag}: Wind surge off did not redraw ({e})")
        # persist ON across reload, then restore default OFF
        nW3 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#windtog")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().windOn === true", arg=nW3, timeout=10000)
        except Exception as e: fail(f"{tag}: Wind surge on (persist) did not redraw ({e})")
        await pg.reload(wait_until="load")
        try:
            await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
            qwl = await pg.evaluate("() => { const q = window.TIDE.qa(), b = document.getElementById('windtog'); return { windOn: q.windOn, pressed: b && b.getAttribute('aria-pressed'), ls: localStorage.getItem('tide:wind'), windTest: q.windTest }; }")
            if not qwl.get("windOn") or qwl.get("pressed") != "true" or qwl.get("ls") != "1":
                fail(f"{tag}: Wind surge on did not survive reload ({qwl})")
            if qwl.get("windTest") is not None and not (qwl.get("windTest") or {}).get("ok"):
                fail(f"{tag}: wind identity failed after reload ({qwl.get('windTest')})")
            # restore default OFF
            nW4 = await pg.evaluate("() => window.__tideDrawn")
            await pg.click("#windtog")
            try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().windOn === false", arg=nW4, timeout=10000)
            except Exception as e: fail(f"{tag}: could not restore Wind surge off ({e})")
            await pg.evaluate("() => localStorage.setItem('tide:wind', '0')")
            print(f"  {tag}: Wind surge toggle off/on/persist ok")
        except Exception as e:
            fail(f"{tag}: reload after Wind surge on failed ({e})")
    if phone:
        sw = await pg.evaluate("document.documentElement.scrollWidth")
        if sw > W + 1: fail(f"{tag}: horizontal overflow scrollWidth={sw} > {W}")
    if SHOT: await pg.screenshot(path=str(Path(SHOT) / f"tide_{tag}.png"))
    if not phone and ok:
        n0 = await pg.evaluate("() => window.__tideDrawn")
        await pg.select_option("#st", "9447130")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().st === '9447130'", arg=n0, timeout=90000)
        except Exception as e: fail(f"{tag}: switching to Seattle did not redraw ({e})")
        await pg.select_option("#days", "7")
        await pg.wait_for_timeout(300)
        try: await pg.wait_for_function("() => { const q = window.TIDE.qa(); return q.st === '9447130' && Math.round((q.end - q.start) / 864e5) === 7; }", timeout=90000)
        except Exception as e: fail(f"{tag}: 7-day range did not apply ({e})")
        if "st=9447130" not in pg.url or "days=7" not in pg.url: fail(f"{tag}: address does not keep station/days ({pg.url})")
        await pg.reload(wait_until="load")
        try:
            await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
            q2 = await pg.evaluate("() => window.TIDE.qa()")
            if q2.get("st") != "9447130" or round((q2["end"] - q2["start"]) / 864e5) != 7: fail(f"{tag}: reload lost station/days ({q2.get('st')})")
        except Exception as e: fail(f"{tag}: reload did not redraw ({e})")
        # state tab: California -> San Francisco default, address + reload keep it, back to Washington restores Seattle
        n0 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#stab button[data-state=ca]")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().st === '9414290'", arg=n0, timeout=90000)
        except Exception as e: fail(f"{tag}: California tab did not open San Francisco ({e})", block=not DATA_DOWN)
        if "state=ca" not in pg.url or "st=9414290" not in pg.url: fail(f"{tag}: address does not keep state=ca / st ({pg.url})")
        pr = await pg.evaluate("() => [...document.querySelectorAll('#stab button')].map(b => b.dataset.state + ':' + b.getAttribute('aria-pressed'))")
        if pr != ["wa:false", "ca:true"]: fail(f"{tag}: state tab pressed states {pr}")
        qca = await pg.evaluate("() => window.TIDE.qa()")
        check_qa(f"{tag} San Francisco", qca, "9414290")
        if sorted(f["k"] for f in qca.get("floods") or []) != ["minor"]: fail(f"{tag}: San Francisco floods {qca.get('floods')} (want verified Minor only)", block=not DATA_DOWN)
        await pg.reload(wait_until="load")
        try:
            await pg.wait_for_function("() => window.__tideDrawn > 0", timeout=90000)
            if (await pg.evaluate("() => [window.TIDE.tab(), window.TIDE.qa().st]")) != ["ca", "9414290"]: fail(f"{tag}: reload lost the California tab")
        except Exception as e: fail(f"{tag}: reload on California did not redraw ({e})")
        n0 = await pg.evaluate("() => window.__tideDrawn")
        await pg.click("#stab button[data-state=wa]")
        try: await pg.wait_for_function("(n) => window.__tideDrawn > n && window.TIDE.qa().st === '9447130'", arg=n0, timeout=90000)
        except Exception as e: fail(f"{tag}: back to Washington did not restore Seattle ({e})")
        if "state=wa" not in pg.url: fail(f"{tag}: address does not show state=wa after switching back ({pg.url})")
        print(f"  {tag}: state tab Washington/California ok")
    real = [e for e in errs if "favicon" not in e]
    if real: fail(f"{tag}: console/page errors: {real[:4]}", block=not DATA_DOWN)
    await ctx.close()

async def main():
    if not B: print(__doc__); sys.exit(1)
    if SHOT: Path(SHOT).mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 1440, "height": 900}); await ctx.route(B + "/**", qa.add_hdr)
        pg = await ctx.new_page(); await pg.goto(B + "/", wait_until="load", timeout=90000)
        btn = await pg.evaluate("() => { const b = document.getElementById('tidebtn'); return b ? (b.getAttribute('onclick') || b.getAttribute('href') || '') + '|' + getComputedStyle(b).display : null; }")
        if not btn or "tide/" not in btn or btn.endswith("|none"): fail(f"map page: Tides button missing or hidden ({btn})")
        await ctx.close()
        await tide_page(br, 1440, 900, 2, False, "desk")
        await tide_page(br, 390, 844, 3, True, "phone")
        table, alias = flood_triple_check()
        old_layout_regressions()
        await stations_check(br, table, alias or {})
        await label_viewports_check(br)
        await br.close()

DATA_DOWN = not noaa_up()
ARCH_DOWN = not arch_up()
if ARCH_DOWN: print("NOTE: GitHub raw (tide-archive) unreachable from this box — archive-load failures are recorded as an outage (not always_block)")
if DATA_DOWN: print("NOTE: NOAA CO-OPS API unreachable from this box — data failures are recorded as an outage (not always_block)")
try: asyncio.run(main())
except SystemExit: raise
except Exception as e: fail(f"guard crashed: {type(e).__name__}: {str(e)[:300]}")
print(f"tide_viewer_guard: {'FAILS ' + str(len(fails)) if fails else 'PASS'}")
if JSON_OUT:
    json.dump({"guard": "tide_viewer", "base": B, "exit": 1 if fails else 0, "fails": [{"msg": m, "always_block": blk} for m, blk in fails]},
              open(JSON_OUT, "w"), indent=1)
sys.exit(1 if fails else 0)
