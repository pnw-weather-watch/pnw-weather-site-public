"""What the browser actually draws: coast, land fill, and data on one rectangle.

Builds a local manifest from the shared camera, serves the site, and opens it
in headless Chromium. A letterboxed coastline fails: its dark pixels no longer
sit on the edge between white land and the ocean color, and a town point is
not on white land.
"""
import io
import json
import os
import sys
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import camera as CAM
import house_style as HS

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = os.path.join(ROOT, "tools", "fast", "site")
def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


REG = read_json(os.path.join(ROOT, "regions", "regions.json"))
ART = os.environ.get("WX_BROWSER_ART", "/opt/cursor/artifacts")
HERE_SHOTS = os.path.join(ROOT, "qa", "layout")

# A point that must fall on land, and one that must fall in the ocean, per view we publish shots for.
CHECKS = {
    "hiw": (("Honolulu", 21.3069, -157.8583), ("51003", 19.151, -160.617)),
    "bigi": (("Hilo", 19.7297, -155.09), ("Kona offshore", 19.50, -156.20)),
    "pnwhr": (("Seattle", 47.6062, -122.3321), ("offshore", 46.2, -126.5)),
    "orco": (("Bend", 44.06, -121.31), ("offshore", 44.0, -126.8)),
    "capasses": (("Redding", 40.5865, -122.3917), ("offshore", 37.2, -125.5)),
    "na": (("Chicago", 41.8781, -87.6298), ("Gulf", 25.5, -90.0)),
}
SHOTS = ("hiw", "orco", "capasses", "pnwhr", "na")
# The whole Pacific loads the entire GSHHG shoreline and is the same camera as every other view.
# North America is included: it is the CONUS-scale check.
BROWSER_VIEWS = tuple(v for v in REG["views"] if v != "pac")


def proj_of(p):
    if p[0] == "merc":
        return ccrs.Mercator(central_longitude=p[1])
    return ccrs.LambertConformal(central_longitude=p[1], central_latitude=p[2], standard_parallels=tuple(p[3]))


def view_of(vid):
    v = dict(REG["views"][vid])
    v["proj"] = proj_of(v["proj"])
    if "ll" in v:
        v["ll"] = tuple(v["ll"])
    if "extent" in v:
        v["extent"] = tuple(v["extent"])
    return v


def land_geom(cam):
    import cartopy.io.shapereader as shpreader
    from shapely.geometry import box
    from shapely.ops import unary_union
    px, py, pw, ph = cam.panel()
    corners = [cam.lonlat(px, py), cam.lonlat(px + pw, py), cam.lonlat(px, py + ph), cam.lonlat(px + pw, py + ph)]
    folds = [lon - 360 if lon > 180 else lon for lon, _ in corners]
    lats = [lat for _, lat in corners]
    bb = box(min(folds) - 1, min(lats) - 1, max(folds) + 1, max(lats) + 1)
    hits = [rec.geometry for rec in shpreader.Reader(shpreader.gshhs("f", 1)).records() if rec.geometry.intersects(bb)]
    return unary_union(hits) if hits else box(0, 0, 0, 0)


def on_land_grid(geom, lon, lat):
    from shapely import contains_xy
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    folded = np.where(lon > 180.0, lon - 360.0, lon)
    return contains_xy(geom, folded, lat)


def label_points(vid):
    if vid == "capasses":
        return [(p["label"], p["lat"], p["lon"]) for p in REG["CA_PASSES"].values()]
    if vid == "orco":
        return [("Astoria", 46.19, -123.83), ("Portland", 45.52, -122.68), ("Bend", 44.06, -121.31),
                ("Eugene", 44.05, -123.09), ("Medford", 42.33, -122.87), ("Ontario", 44.03, -116.96)]
    if vid == "na":
        return [("Seattle", 47.61, -122.33), ("Chicago", 41.88, -87.63), ("Denver", 39.74, -104.99)]
    return []


def write_town_labels(vid, path):
    """Names from the same camera as the coast, so the screenshot can be read."""
    from PIL import ImageDraw, ImageFont
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    pts = label_points(vid)
    if not pts:
        im.save(path)
        return
    cam = CAM.Camera(view_of(vid))
    try:
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        px, py, pw, ph = cam.panel()
        placed = []
        offsets = [(14, 0), (100, 0), (-110, 0), (14, -28), (14, 28), (180, -12), (-180, 12)]
        for name, lat, lon in sorted(pts, key=lambda p: -p[1]):
            x, y = cam.pixel(lon, lat)
            if not (px - 4 <= x <= px + pw + 4 and py - 4 <= y <= py + ph + 4):
                continue
            ox, oy = offsets[0]
            for ox, oy in offsets:
                if not any(abs(x + ox - qx) < 96 and abs(y + oy - qy) < 26 for qx, qy in placed):
                    break
            placed.append((x + ox, y + oy))
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                draw.text((x + ox + dx, y + oy + dy), name, font=font, fill=(255, 255, 255, 230))
            draw.text((x + ox, y + oy), name, font=font, fill=(20, 22, 26, 255))
    finally:
        cam.close()
    im.save(path)


def save_png(fig, path):
    fig.savefig(path, dpi=100, transparent=True)
    plt.close(fig)


def write_layers(vid, out_dir):
    """Land fill and coast strokes, each from the same full-canvas camera."""
    os.makedirs(out_dir, exist_ok=True)
    cam = CAM.Camera(view_of(vid))
    cam.fig.patch.set_alpha(0)
    cam.ax.patch.set_alpha(0)
    HS.land(cam.ax, cf)
    HS.frame(cam.ax)
    cam.snap()
    cam.fig.savefig(os.path.join(out_dir, f"land_{vid}.png"), dpi=100, transparent=True)
    cam.close()
    cam = CAM.Camera(view_of(vid))
    cam.fig.patch.set_alpha(0)
    cam.ax.patch.set_alpha(0)
    HS.outlines(cam.ax, cf, states=True)
    HS.frame(cam.ax)
    cam.snap()
    cam.fig.savefig(os.path.join(out_dir, f"base_{vid}.png"), dpi=100, transparent=True)
    cam.close()
    write_town_labels(vid, os.path.join(out_dir, f"towns_{vid}.png"))


def ll_pack(cam, geom, res=0.05):
    """Fine lat/lon field so the land sentinel follows the GSHHG edge, not a 0.25 deg block."""
    g = CAM.sample_grid(cam, 8, res)
    fi, fj = g["fi"], g["fj"]
    ok = np.isfinite(fi) & np.isfinite(fj)
    i0 = int(np.floor(fi[ok].min())) - 1
    i1 = int(np.ceil(fi[ok].max())) + 2
    j0 = int(np.floor(fj[ok].min())) - 1
    j1 = int(np.ceil(fj[ok].max())) + 2
    ny, nx = i1 - i0, j1 - j0
    lat = 90.0 - (i0 + np.arange(ny)) * res
    lon = ((j0 + np.arange(nx)) * res) % 360.0
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    field = np.where(on_land_grid(geom, LO, LA), -0.5, 12.0).astype(np.float32)
    lut = np.stack([fi - i0, fj - j0, g["ang"]], -1).astype("<f4")
    return field, lut, ny, nx, g


def lcc_pack(cam, geom):
    hp = ccrs.LambertConformal(central_longitude=-97.5, central_latitude=38.5, standard_parallels=(38.5, 38.5))
    pc = ccrs.PlateCarree()
    px, py, pw, ph = cam.panel()
    corners = [cam.lonlat(px + 2, py + 2), cam.lonlat(px + pw - 2, py + 2),
               cam.lonlat(px + 2, py + ph - 2), cam.lonlat(px + pw - 2, py + ph - 2)]
    xy = [hp.transform_point(lon - 360 if lon > 180 else lon, lat, pc) for lon, lat in corners]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    d = 3000.0
    gx0, gy0 = min(xs) - 4 * d, min(ys) - 4 * d
    nx = int((max(xs) - gx0) / d) + 8
    ny = int((max(ys) - gy0) / d) + 8

    def to_ij(lon, lat):
        folded = np.where(np.asarray(lon) > 180.0, np.asarray(lon) - 360.0, lon)
        hh = hp.transform_points(pc, folded, lat)
        return (hh[..., 1] - gy0) / d, (hh[..., 0] - gx0) / d

    g = CAM.sample_grid(cam, 8, to_ij=to_ij)
    xs = gx0 + np.arange(nx) * d
    ys = gy0 + np.arange(ny) * d
    XX, YY = np.meshgrid(xs, ys)
    ll = pc.transform_points(hp, XX, YY)
    field = np.where(on_land_grid(geom, ll[..., 0], ll[..., 1]), -100.0, 55.0).astype(np.float32)
    lut = np.stack([g["fi"], g["fj"], g["ang"]], -1).astype("<f4")
    return field, lut, ny, nx, g


def _dilate(mask, n):
    out = mask.copy()
    for k in range(1, n + 1):
        out[k:, :] |= mask[:-k, :]
        out[:-k, :] |= mask[k:, :]
        out[:, k:] |= mask[:, :-k]
        out[:, :-k] |= mask[:, k:]
    return out


def _near(mask, x, y, r):
    y0, y1 = max(0, y - r), min(mask.shape[0], y + r + 1)
    x0, x1 = max(0, x - r), min(mask.shape[1], x + r + 1)
    return bool(mask[y0:y1, x0:x1].any())


def write_field(path, field, lo, hi):
    q = np.clip(np.rint((field - lo) / (hi - lo) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(q, "L").save(path)


def write_letter_coast(vid, path):
    """The production failure, as a full-canvas PNG: shores still in the old inner rectangle.

    Live Hawaii measured that rectangle at about x 420-1500, y 390-1000 of the 1920-wide frame.
    """
    v = view_of(vid)
    fig = plt.figure(figsize=HS.SCREEN_IN, dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([420 / 1920, (1080 - 1000) / 1080, (1500 - 420) / 1920, (1000 - 390) / 1080], projection=v["proj"])
    if "extent" in v:
        ax.set_extent(v["extent"], crs=v["proj"])
    else:
        ax.set_extent(v["ll"], crs=ccrs.PlateCarree())
    HS.outlines(ax, cf, states=True)
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_edgecolor("#8a909a")
        s.set_linewidth(1.2)
    fig.savefig(path, dpi=100, transparent=True)
    plt.close(fig)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def log_message(self, fmt, *args):
        return


class BrowserLayers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = os.path.join(ROOT, "tools", "fast", "site", "_browser_data")
        if os.environ.get("WX_BROWSER_REUSE") and os.path.exists(os.path.join(cls.data, "manifest.json")):
            cls._serve()
            return
        os.makedirs(os.path.join(cls.data, "static"), exist_ok=True)
        views_ll, views_lcc = {}, {}
        products = {
            "waves": {"title": "Significant Wave Height", "fields": ["swh"], "fill": "swh",
                      "levels": [0, 40], "colors": ["#1a6ea8"], "min_show": 0, "ticks": [0, 40], "towns": "numbers",
                      "extra": "local", "pct": [0, 100]},
            "t2m": {"title": "2 m Temperature", "fields": ["t2m"], "fill": "t2m",
                    "levels": [-40, 120], "colors": ["#3d8c40"], "min_show": -80, "ticks": [-40, 120], "towns": "numbers",
                    "extra": "local", "pct": [0, 100], "mask_edge": True},
        }
        for vid in BROWSER_VIEWS:
            print(f"build {vid}", flush=True)
            raw = REG["views"][vid]
            cam = CAM.Camera(view_of(vid))
            geom = land_geom(cam)
            write_layers(vid, os.path.join(cls.data, "static"))
            lcc = raw["proj"][0] == "lcc"
            if lcc:
                field, lut, ny, nx, g = lcc_pack(cam, geom)
                model, name, lo, hi = "hrrr", "t2m", -100.0, 120.0
                bucket = views_lcc
            else:
                field, lut, ny, nx, g = ll_pack(cam, geom)
                model, name, lo, hi = "ifs", "swh", -0.5, 20.0
                bucket = views_ll
            lut.tofile(os.path.join(cls.data, "static", f"lut_{model}_{vid}.bin"))
            run_dir = os.path.join(cls.data, "runs", model, "2026110612", "single")
            os.makedirs(run_dir, exist_ok=True)
            write_field(os.path.join(run_dir, f"{name}_{vid}.png"), field, lo, hi)
            bucket[vid] = dict(label=raw["label"], fig=[1920, 1080], panel=list(cam.panel()),
                               stride=8, nx=int(g["nx"]), ny=int(g["ny"]),
                               lut=f"static/lut_{model}_{vid}.bin",
                               towns_png=f"static/towns_{vid}.png", cut=[0, ny, 0, nx], towns=[],
                               anchors=cam.anchors(),
                               grid_ny=ny, grid_nx=nx, field_file=f"{name}_{vid}.png")
            cam.close()
        def run(model, field, lo, hi):
            return {"model": model, "cycle": "2026110612", "init": "2026-11-06T12:00:00+00:00",
                    "base": f"runs/{model}/2026110612", "fields": [field],
                    "grid": {"ny": 10, "nx": 10},
                    "runline": "local build", "complete": True, "file": "single/{name}_f{f:03d}.png",
                    "steps": [{"f": 3, "valid": "2026-11-06T15:00:00Z", "valid_line": "Valid Fri 11-6 · 7 AM PT",
                               "badge": ["F+3", "12Z FRI"], "ranges": {field: [lo, hi]}}]}
        man = {"static_v": "canvas",
               "style": {"BG": "#15171c", "INK": "#f4f2ee", "MUTED": "#a7abb3", "ACCENT": "#ffc970", "LAND": "#ffffff"},
               "runs": {"ifs": ["2026110612"], "hrrr": ["2026110612"]},
               "models": {
                   "ifs": {"name": "ECMWF IFS", "site": "ECMWF 0.25°", "res": "0.25°", "grid": "ll",
                           "views": views_ll, "products": {"waves": products["waves"]}},
                   "hrrr": {"name": "NOAA HRRR", "site": "HRRR", "res": "3 km", "grid": "lcc",
                            "views": views_lcc, "products": {"t2m": products["t2m"]}},
               }}
        write_json(os.path.join(cls.data, "manifest.json"), man)
        os.makedirs(os.path.join(cls.data, "runs", "ifs", "2026110612"), exist_ok=True)
        os.makedirs(os.path.join(cls.data, "runs", "hrrr", "2026110612"), exist_ok=True)
        write_json(os.path.join(cls.data, "runs", "ifs", "2026110612", "run.json"), run("ifs", "swh", -0.5, 20))
        write_json(os.path.join(cls.data, "runs", "hrrr", "2026110612", "run.json"), run("hrrr", "t2m", -100, 120))
        cls._serve()

    @classmethod
    def _serve(cls):
        link = os.path.join(SITE, "data")
        if os.path.islink(link) or os.path.exists(link):
            os.remove(link) if os.path.islink(link) or os.path.isfile(link) else None
        if not os.path.exists(link):
            os.symlink(cls.data, link)
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        link = os.path.join(SITE, "data")
        if os.path.islink(link):
            os.remove(link)

    def _manifest(self, static_v):
        path = os.path.join(self.data, "manifest.json")
        man = read_json(path)
        man["static_v"] = static_v
        write_json(path, man)

    def _shoot(self, page, vid):
        import base64
        lcc = REG["views"][vid]["proj"][0] == "lcc"
        model, prod = ("hrrr", "t2m") if lcc else ("ifs", "waves")
        man = read_json(os.path.join(self.data, "manifest.json"))
        V = man["models"][model]["views"][vid]
        run_path = os.path.join(self.data, "runs", model, "2026110612", "run.json")
        run = read_json(run_path)
        run["grid"] = {"ny": V["grid_ny"], "nx": V["grid_nx"]}
        # A shared filename stays in the viewer's pixel cache, so each view needs its own file.
        run["file"] = "single/" + V["field_file"]
        cycle = "2026110612" + vid
        run["base"] = f"runs/{model}/2026110612"
        dest = os.path.join(self.data, "runs", model, cycle)
        os.makedirs(dest, exist_ok=True)
        write_json(os.path.join(dest, "run.json"), run)
        man = read_json(os.path.join(self.data, "manifest.json"))
        man["runs"].setdefault(model, [])
        if cycle not in man["runs"][model]:
            man["runs"][model].append(cycle)
            write_json(os.path.join(self.data, "manifest.json"), man)
        url = f"http://127.0.0.1:{self.port}/index.html?prod={prod}&view={vid}&run={model}/{cycle}&x1=1&bare=1"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_function("() => window.__drawn && window.__drawn.indexOf('" + vid + "') >= 0", timeout=60000)
        page.wait_for_timeout(250)
        data = page.evaluate("() => document.getElementById('map').toDataURL('image/png').split(',')[1]")
        im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        self.assertEqual(im.size, (1920, 1080), vid)
        return im

    def test_browser_layers_share_one_rectangle(self):
        os.makedirs(ART, exist_ok=True)
        os.makedirs(HERE_SHOTS, exist_ok=True)
        static = os.path.join(self.data, "static")
        for vid in SHOTS:
            good = os.path.join(static, f"base_{vid}.png")
            os.replace(good, good + ".full")
            write_letter_coast(vid, good)
        fails = []
        try:
            self._run_browser(fails, static)
        finally:
            for vid in SHOTS:
                good = os.path.join(static, f"base_{vid}.png")
                full = good + ".full"
                if os.path.exists(full):
                    os.replace(full, good)
        self.assertFalse(fails, "\n".join(fails))

    def _prepare_runs(self):
        """One run file per view so the browser cannot reuse another view's grid."""
        man = read_json(os.path.join(self.data, "manifest.json"))
        for vid in BROWSER_VIEWS:
            lcc = REG["views"][vid]["proj"][0] == "lcc"
            model = "hrrr" if lcc else "ifs"
            field, lo, hi = ("t2m", -100, 120) if lcc else ("swh", -0.5, 20)
            V = man["models"][model]["views"][vid]
            cycle = "2026110612" + vid
            run = {"model": model, "cycle": cycle, "init": "2026-11-06T12:00:00+00:00",
                   "base": f"runs/{model}/2026110612", "fields": [field],
                   "grid": {"ny": V["grid_ny"], "nx": V["grid_nx"]},
                   "runline": "local build", "complete": True, "file": "single/" + V["field_file"],
                   "steps": [{"f": 3, "valid": "2026-11-06T15:00:00Z", "valid_line": "Valid Fri 11-6 · 7 AM PT",
                              "badge": ["F+3", "12Z FRI"], "ranges": {field: [lo, hi]}}]}
            dest = os.path.join(self.data, "runs", model, cycle)
            os.makedirs(dest, exist_ok=True)
            write_json(os.path.join(dest, "run.json"), run)
            man["runs"].setdefault(model, [])
            if cycle not in man["runs"][model]:
                man["runs"][model].append(cycle)
        write_json(os.path.join(self.data, "manifest.json"), man)

    def _run_browser(self, fails, static):
        from playwright.sync_api import sync_playwright
        self._prepare_runs()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.on("pageerror", lambda e: fails.append(f"page: {e}"))
            self._manifest("letter")
            for vid in SHOTS:
                im = self._shoot(page, vid)
                im.save(os.path.join(ART, f"before_{vid}_1920x1080.png"))
                im.save(os.path.join(HERE_SHOTS, f"before_{vid}_1920x1080.png"))
                why = self._check(im, vid)
                print(f"before {vid}: {why or 'NOT DETECTED'}", flush=True)
                if not why:
                    fails.append(f"{vid}: letterboxed coast was not detected")
            for vid in SHOTS:
                good = os.path.join(static, f"base_{vid}.png")
                os.replace(good + ".full", good)
            browser.close()
            self._manifest("full")
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.on("pageerror", lambda e: fails.append(f"page: {e}"))
            every = os.path.join(HERE_SHOTS, "browser")
            os.makedirs(every, exist_ok=True)
            for vid in BROWSER_VIEWS:
                im = self._shoot(page, vid)
                im.save(os.path.join(every, f"{vid}.png"))
                if vid in SHOTS:
                    im.save(os.path.join(ART, f"after_{vid}_1920x1080.png"))
                    im.save(os.path.join(HERE_SHOTS, f"after_{vid}_1920x1080.png"))
                why = self._check(im, vid)
                print(f"after {vid}: {why or 'ok'}", flush=True)
                if why:
                    fails.append(f"{vid}: {why}")
            browser.close()

    def _check(self, im, vid):
        a = np.asarray(im)
        r = a[:, :, 0].astype(int)
        g = a[:, :, 1].astype(int)
        b = a[:, :, 2].astype(int)
        white = (r > 230) & (g > 230) & (b > 230)
        if REG["views"][vid]["proj"][0] == "lcc":
            ocean = (g > 90) & (g > r + 15) & (g > b + 15)
        else:
            ocean = (np.abs(r - 26) < 45) & (b > 120) & (g > 60)
        # A floating inner frame is a long straight gray stroke with ocean on both sides.
        # State lines and the coast sit on land, so they do not count.
        spine = (np.abs(r - 138) < 22) & (np.abs(g - 144) < 22) & (np.abs(b - 154) < 22) & (np.abs(b - r) < 30)
        floating = np.zeros(spine.shape, bool)
        floating[2:-2] = spine[2:-2] & ocean[:-4] & ocean[4:]
        longest = 0
        for row in floating[140:1000]:
            run = 0
            for v in row:
                run = run + 1 if v else 0
                if run > longest:
                    longest = run
        if longest > 80:
            return "inner rectangle is still drawn"
        bg = (r < 40) & (g < 40) & (b < 40)
        ink = ~white & ~ocean & ~bg
        ink[:130, :] = False
        ink[1000:, :] = False
        cam = CAM.Camera(view_of(vid))
        try:
            if vid in CHECKS:
                (tn, tlat, tlon), (bn, blat, blon) = CHECKS[vid]
                x, y = (int(round(v)) for v in cam.pixel(tlon, tlat))
                if ocean[y, x] or not _near(white, x, y, 10):
                    return f"{tn} is not on white land"
                x, y = (int(round(v)) for v in cam.pixel(blon, blat))
                if not ocean[y, x]:
                    return f"{bn} is not on the ocean"
            # The coast stroke sits between land and ocean, so the two colors may not touch.
            edge = _dilate(white, 3) & _dilate(ocean, 3)
            ys, xs = np.where(edge)
            if len(xs) < 40 or int(ink.sum()) < 40:
                return "coast or land edge missing"
            step = max(1, len(xs) // 240)
            half = 12
            H, W = ink.shape
            far = 0
            take = list(zip(xs[::step], ys[::step]))
            for x, y in take:
                y0, y1 = max(0, y - half), min(H, y + half + 1)
                x0, x1 = max(0, x - half), min(W, x + half + 1)
                if not ink[y0:y1, x0:x1].any():
                    far += 1
            if far / len(take) > 0.15:
                return "coastline is off the land edge"
        finally:
            cam.close()
        return ""


class TrueShape(unittest.TestCase):
    def test_every_view_is_conformal_and_fills_the_slot(self):
        import math
        slot_aspect = None
        for vid in REG["views"]:
            self.assertIn(REG["views"][vid]["proj"][0], ("lcc", "merc"), vid)
            cam = CAM.Camera(view_of(vid))
            try:
                lon, lat = cam.lonlat(960, 540)
                x0, y0 = cam.pixel(lon, lat)
                x1, y1 = cam.pixel(lon, lat + 0.5)
                x2, y2 = cam.pixel(lon + 0.5, lat)
                dlat = math.hypot(x1 - x0, y1 - y0)
                dlon = math.hypot(x2 - x0, y2 - y0)
                self.assertGreater(dlat, 1, vid)
                self.assertAlmostEqual(dlon / (dlat * math.cos(math.radians(lat))), 1.0, delta=0.025, msg=vid)
                dx = abs(cam.xlim[1] - cam.xlim[0])
                dy = abs(cam.ylim[1] - cam.ylim[0])
                slot = HS.screen_layout(cam.fig)["axes"]
                aspect = (slot[2] * HS.SCREEN_IN[0]) / (slot[3] * HS.SCREEN_IN[1])
                slot_aspect = aspect
                self.assertAlmostEqual(dx / dy, aspect, delta=0.03, msg=vid)
                # the painted map is the full slot: no inset axes
                pos = cam.position
                self.assertAlmostEqual(pos[0], 0.0, delta=0.01, msg=vid)
                self.assertAlmostEqual(pos[2], 1.0, delta=0.01, msg=vid)
            finally:
                cam.close()
        self.assertIsNotNone(slot_aspect)


class LayerSource(unittest.TestCase):
    def test_static_rewrites_the_full_canvas_layers(self):
        with open(os.path.join(ROOT, "tools", "fast", "fast_encode.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("Always rewrite land and coast", src)
        self.assertNotIn('if not os.path.exists(f"{out}/static/base_{vid}.png")', src)
        with open(os.path.join(SITE, "viewer.js"), encoding="utf-8") as f:
            view = f.read()
        self.assertIn("WAVE_PIDS.test(pid) && v < 0", view)
        self.assertIn("maskSea", view)
        self.assertIn("ctx.drawImage(st.land, 0, 0, LW, LH)", view)


if __name__ == "__main__":
    unittest.main()
