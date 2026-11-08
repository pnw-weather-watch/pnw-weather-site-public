"""Headless viewer against the preview/ layout.

preview/ currently holds a slim index, per-model catalogs, a handful of WebP
samples, and the previous PNGs plus the full manifest.json. The page has to
fill Runs, Product and View from that, and paint a frame. A missing, partial
or unreadable index or catalog must use the full manifest instead.
"""
import json
import os
import shutil
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
from PIL import Image

import fast_encode as fe

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = os.path.join(ROOT, "tools", "fast", "site")
MODELS = ["hrrr", "rrfs", "nbm", "gfs", "ifs", "ifs9", "aifs", "eps", "aens", "gfsw", "oisst"]
CYCLE = "2026110718"
RUN = f"hrrr/{CYCLE}"


def _product():
    return {"title": "2 m Temperature", "fields": ["t2m"], "fill": "t2m", "levels": [0, 50, 100],
            "colors": ["#2040a0", "#3d8c40"], "towns": "none", "extra": "{lo} to {hi} F", "pct": [5, 95]}


def _view():
    # 160x90 is 16:9, so the header takes the screen-frame path and does not need size_in.
    return {"label": "Test box", "fig": [160, 90], "panel": [0, 0, 160, 90], "stride": 4,
            "nx": 41, "ny": 24, "lut": "static/lut_hrrr_box.bin", "towns_png": "static/towns_box.png", "towns": []}


def _manifest():
    models = {}
    for mid in MODELS:
        models[mid] = {"name": mid, "site": mid.upper(), "res": "3 km", "grid": "ll", "note": "",
                       "crop": [10, 20, 30, 40], "views": {"box": _view()}, "products": {"t2m": _product()}}
    models["hrrr"]["site"] = "HRRR"
    models["hrrr"]["name"] = "NOAA HRRR"
    return {"static_v": "previewfix", "style": {"BG": "#15171c", "INK": "#f4f2ee", "MUTED": "#a7abb3", "ACCENT": "#ffc970", "LAND": "#ffffff"},
            "runs": {"hrrr": [CYCLE]}, "models": models}


def _frames(run_dir):
    single = os.path.join(run_dir, "single")
    os.makedirs(single, exist_ok=True)
    rgb = np.zeros((2, 2, 3), np.uint8)
    rgb[..., 0] = 180
    im = Image.fromarray(rgb, "RGB")
    im.save(os.path.join(single, "t2m_f001.webp"), format="WEBP", lossless=True, quality=100, method=4)
    im.save(os.path.join(single, "t2m_f001.png"), format="PNG")
    for i in range(1, 12):
        im.save(os.path.join(single, f"sample_{i:02d}.webp"), format="WEBP", lossless=True, quality=100, method=4)
        im.save(os.path.join(single, f"old_{i:02d}.png"), format="PNG")


def _page(path):
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as f:
        html = f.read()
    html = html.replace('<script src="viewer.js', '<script>window.WX_DATA="/d/"</script><script src="viewer.js', 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        rel = self.path.split("?", 1)[0].lstrip("/")
        root = self.server.root
        fp = os.path.normpath(os.path.join(root, rel))
        if not fp.startswith(root) or not os.path.isfile(fp):
            self.send_error(404)
            return
        with open(fp, "rb") as f:
            data = f.read()
        if rel == "d/manifest.index.json" and self.server.break_index:
            # Same failure the preview function produced: Content-Encoding says gzip, the body is not.
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        import mimetypes
        ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        return


class PreviewViewer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import mimetypes
        mimetypes.add_type("image/webp", ".webp")
        cls.tmp = os.path.join(ROOT, "tools", "fast", "site", "_preview_fixture")
        shutil.rmtree(cls.tmp, ignore_errors=True)
        os.makedirs(cls.tmp)
        for name in ("viewer.js", "selection.js", "cameras.js", "coastline.js", "theme.css", "reqbox.js"):
            shutil.copy(os.path.join(SITE, name), os.path.join(cls.tmp, name))
        _page(os.path.join(cls.tmp, "index.html"))
        data = os.path.join(cls.tmp, "d")
        cls.man = _manifest()
        os.makedirs(data)
        with open(os.path.join(data, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(cls.man, f)
        fe.write_catalogs(cls.man, data)
        with open(os.path.join(data, "manifest.index.json"), "rb") as f:
            cls.good_index = f.read()
        with open(os.path.join(data, "models", "hrrr.json"), "rb") as f:
            cls.good_hrrr = f.read()
        os.makedirs(os.path.join(data, "static"))
        nx, ny = 41, 24
        lut = np.zeros((ny, nx, 3), np.float32)
        lut[..., 0] = 0.5
        lut[..., 1] = 0.5
        lut.tofile(os.path.join(data, "static", "lut_hrrr_box.bin"))
        Image.new("RGBA", (160, 90), (0, 0, 0, 0)).save(os.path.join(data, "static", "base_box.png"))
        fixes = {"models": {"gfs": {"box": {"towns": [{"name": "Seattle", "kind": "town", "x": 0.2, "y": 0.2, "fi": 0, "fj": 0, "size": 12, "color": "#111"}],
                                            "towns_png": "static/towns_box.png"}}}}
        with open(os.path.join(data, "static", "view_fixes.json"), "w", encoding="utf-8") as f:
            json.dump(fixes, f)
        run_dir = os.path.join(data, "runs", "hrrr", CYCLE)
        os.makedirs(run_dir)
        run = {"model": "hrrr", "cycle": CYCLE, "init": "2026-11-07T18:00:00+00:00", "base": f"runs/hrrr/{CYCLE}",
               "fields": ["t2m"], "grid": {"ny": 2, "nx": 2}, "runline": "HRRR 18Z 11-07", "complete": True,
               "file": "single/{name}_f{f:03d}.webp",
               "steps": [{"f": 1, "valid": "2026-11-07T19:00:00Z", "valid_line": "Valid", "badge": ["F+1", "18Z"],
                          "ranges": {"t2m": [0, 100]}}]}
        with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
            json.dump(run, f)
        _frames(run_dir)
        webps = [n for n in os.listdir(os.path.join(run_dir, "single")) if n.endswith(".webp")]
        pngs = [n for n in os.listdir(os.path.join(run_dir, "single")) if n.endswith(".png")]
        catalogs = os.listdir(os.path.join(data, "models"))
        if len(webps) != 12 or len(pngs) < 12 or len(catalogs) != 11:
            raise AssertionError(f"fixture layout webp={len(webps)} png={len(pngs)} catalogs={len(catalogs)}")
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.httpd.root = cls.tmp
        cls.httpd.break_index = False
        cls.port = cls.httpd.server_address[1]
        cls.httpd.daemon_threads = True
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        from playwright.sync_api import sync_playwright
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.httpd.shutdown()
        cls.httpd.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        data = os.path.join(self.tmp, "d")
        self.httpd.break_index = False
        with open(os.path.join(data, "manifest.index.json"), "wb") as f:
            f.write(self.good_index)
        with open(os.path.join(data, "models", "hrrr.json"), "wb") as f:
            f.write(self.good_hrrr)

    def _open(self):
        page = self.browser.new_page(viewport={"width": 1100, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        reqs = []
        page.on("request", lambda r: reqs.append(r.url.split("?", 1)[0]))
        page.goto(f"http://127.0.0.1:{self.port}/index.html?prod=t2m&view=box&x1=1", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_function("() => window.__ready || window.__bootError", timeout=20000)
        state = page.evaluate("""() => {
          const c = document.getElementById('map');
          const g = c.getContext('2d');
          const x = Math.floor(c.width / 2), y = Math.floor(c.height / 2);
          const p = g.getImageData(x, y, 1, 1).data;
          const opts = id => [...document.getElementById(id).options].map(o => o.value).filter(Boolean);
          return {drawn: window.__drawn || '', err: window.__bootError || '',
                  runs: opts('run'), prods: opts('prod'), views: opts('view'),
                  px: [p[0], p[1], p[2], p[3]], w: c.width, h: c.height,
                  catalog: !!(S.man && S.man.catalog_v),
                  title: S.man && S.man.models && S.man.models.hrrr && S.man.models.hrrr.products && S.man.models.hrrr.products.t2m && S.man.models.hrrr.products.t2m.title};
        }""")
        page.close()
        state["errors"] = errors
        state["reqs"] = reqs
        return state

    def _assert_drawn(self, state):
        self.assertIn(RUN, state["runs"], state)
        self.assertIn("t2m", state["prods"], state)
        self.assertIn("box", state["views"], state)
        self.assertTrue(state["drawn"], state)
        r, g, b, a = state["px"]
        self.assertGreater(g, 100, state)
        self.assertGreater(g, r + 30, state)
        self.assertGreater(g, b + 30, state)
        self.assertEqual(state["title"], "2 m Temperature", state)
        self.assertFalse(state["err"], state)

    def test_preview_layout_fills_menus_and_draws(self):
        state = self._open()
        self._assert_drawn(state)
        self.assertTrue(state["catalog"], state)
        urls = state["reqs"]
        self.assertTrue(any(u.endswith("/d/manifest.index.json") for u in urls), urls)
        self.assertTrue(any(u.endswith("/d/models/hrrr.json") for u in urls), urls)
        self.assertTrue(any(u.endswith("/d/static/view_fixes.json") for u in urls), urls)
        self.assertTrue(any(u.endswith("t2m_f001.webp") for u in urls), urls)
        self.assertFalse(any(u.endswith("/d/manifest.json") for u in urls), urls)

    def test_partial_catalog_uses_the_full_manifest(self):
        with open(os.path.join(self.tmp, "d", "models", "hrrr.json"), "w", encoding="utf-8") as f:
            f.write('{"note":"partial"}')
        state = self._open()
        self._assert_drawn(state)
        self.assertFalse(state["catalog"], state)
        self.assertTrue(any(u.endswith("/d/manifest.json") for u in state["reqs"]), state["reqs"])

    def test_unreadable_index_uses_the_full_manifest(self):
        with open(os.path.join(self.tmp, "d", "manifest.index.json"), "w", encoding="utf-8") as f:
            f.write('{"catalog_v":1')
        state = self._open()
        self._assert_drawn(state)
        self.assertFalse(state["catalog"], state)
        self.assertTrue(any(u.endswith("/d/manifest.json") for u in state["reqs"]), state["reqs"])

    def test_gzip_index_decode_failure_uses_the_full_manifest(self):
        self.httpd.break_index = True
        state = self._open()
        self._assert_drawn(state)
        self.assertFalse(state["catalog"], state)
        self.assertTrue(any(u.endswith("/d/manifest.json") for u in state["reqs"]), state["reqs"])


if __name__ == "__main__":
    unittest.main()
