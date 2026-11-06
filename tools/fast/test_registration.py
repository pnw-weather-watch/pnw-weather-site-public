"""Data raster and coastlines share one axes rectangle on every view.

The 1920x1080 layout used to letterbox the basemap inside the frame while the
data panel stayed a different size. Each view now fills the slot between the
color bar and the timestamp, and a known point projects to the same pixel the
encoder's lookup table would use.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import cartopy.crs as ccrs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import house_style as HS
from camera import Camera, cell_ij, half_cell_edges, sample_grid

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
REGIONS = os.path.join(ROOT, "regions", "regions.json")
# A place that must fall inside the view, and on the pixel the map says it does.
POINTS = {
    "na": ("Denver", 39.7392, -104.9903),
    "pac": ("Honolulu", 21.3069, -157.8583),
    "pnw": ("Seattle", 47.6062, -122.3321),
    "pnwt": ("Seattle", 47.6062, -122.3321),
    "pnwhr": ("Seattle", 47.6062, -122.3321),
    "passes": ("Snoqualmie", 47.4245, -121.4136),
    "ca": ("Sacramento", 38.5816, -121.4944),
    "socal": ("Los Angeles", 34.0522, -118.2437),
    "cenca": ("Fresno", 36.7378, -119.7871),
    "norca": ("Redding", 40.5865, -122.3917),
    "capasses": ("Donner", 39.33987, -120.34396),
    "hiw": ("Honolulu", 21.3069, -157.8583),
    "bay": ("San Francisco", 37.7749, -122.4194),
    "orco": ("Newport", 44.6368, -124.0535),
    "bigi": ("Hilo", 19.7297, -155.09),
}


def proj_of(p):
    if p[0] == "merc":
        return ccrs.Mercator(central_longitude=p[1])
    return ccrs.LambertConformal(central_longitude=p[1], central_latitude=p[2], standard_parallels=tuple(p[3]))


def view_dict(v):
    d = dict(v)
    d["proj"] = proj_of(v["proj"])
    if "ll" in v:
        d["ll"] = tuple(v["ll"])
    if "extent" in v:
        d["extent"] = tuple(v["extent"])
    return d


def open_view(v):
    cam = Camera(view_dict(v))
    return cam.fig, cam.ax, cam.layout


class Registration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(REGIONS, encoding="utf-8") as f:
            cls.views = json.load(f)["views"]

    def test_every_view_fills_the_map_slot(self):
        for vid, v in self.views.items():
            fig, ax, lay = open_view(v)
            pos = ax.get_position().bounds
            want = lay["axes"]
            for i in range(4):
                self.assertAlmostEqual(float(pos[i]), float(want[i]), places=2, msg=vid)
            plt.close(fig)

    def test_known_point_matches_the_lookup_pixel(self):
        for vid, (name, lat, lon) in POINTS.items():
            fig, ax, lay = open_view(self.views[vid])
            fig.set_dpi(100)
            fig.canvas.draw()
            W, H = fig.get_size_inches() * 100
            b = ax.get_position()
            px, py, pw, ph = b.x0 * W, (1 - b.y1) * H, b.width * W, b.height * H
            # encoder LUT: panel pixel -> projected x,y -> lon/lat
            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            # the town in display pixels, the same way cartopy draws the coastline
            disp = ax.transData.transform(ax.projection.transform_point(lon, lat, ccrs.PlateCarree()))
            # and via the LUT formula (projected x from the lon/lat, then into the panel)
            xx, yy = ax.projection.transform_point(lon, lat, ccrs.PlateCarree())
            lut_x = px + (xx - x0) / (x1 - x0) * pw
            lut_y = py + (y1 - yy) / (y1 - y0) * ph
            # display y is from the bottom; the LUT y above is from the top of the figure
            disp_x, disp_y_bottom = disp
            lut_y_bottom = H - lut_y
            self.assertLess(abs(disp_x - lut_x), 1.5, f"{vid} {name} x")
            self.assertLess(abs(disp_y_bottom - lut_y_bottom), 1.5, f"{vid} {name} y")
            # inside the map, not in the color-bar or timestamp strip
            self.assertGreater(disp_x, px - 1, vid)
            self.assertLess(disp_x, px + pw + 1, vid)
            self.assertGreater(disp_y_bottom, H - (py + ph) - 1, vid)
            self.assertLess(disp_y_bottom, H - py + 1, vid)
            plt.close(fig)


# Products that must share one camera. Waves leave land unpainted so the GSHHG fill shows.
PRODUCTS = ("t2m", "waves", "wavemax", "snow")
HI_BUOY = ("51003", 19.151, -160.617)          # Western Hawaii, open ocean on hiw
BIGI_OFFSHORE = ("offshore", 19.50, -156.20)   # just west of the Big Island
WC_TOWN = ("San Francisco", 37.7749, -122.4194)
WC_BUOY = ("46026", 37.75, -122.838)


def land_geometry(west, east, south, north):
    """GSHHG full land polygons inside a lon/lat box. Lons are -180..180."""
    import cartopy.io.shapereader as shpreader
    from shapely.geometry import box
    from shapely.ops import unary_union
    bb = box(west - 0.4, south - 0.4, east + 0.4, north + 0.4)
    hits = []
    for rec in shpreader.Reader(shpreader.gshhs("f", 1)).records():
        if rec.geometry.intersects(bb):
            hits.append(rec.geometry)
    return unary_union(hits) if hits else box(0, 0, 0, 0)


def crosses_dateline(v):
    ll = v.get("ll")
    return bool(ll) and ll[0] < -180


class SharedCamera(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(REGIONS, encoding="utf-8") as f:
            cls.views = json.load(f)["views"]

    def test_every_view_and_product_share_one_camera(self):
        for vid, v in self.views.items():
            a, b = Camera(view_dict(v)), Camera(view_dict(v))
            self.assertEqual(a.size(), (1920.0, 1080.0), vid)
            self.assertEqual(b.size(), a.size(), vid)
            for i in range(4):
                self.assertAlmostEqual(a.bounds()[i], b.bounds()[i], places=3, msg=vid)
                self.assertAlmostEqual(a.position[i], a.layout["axes"][i], places=3, msg=vid)
            # the data rectangle is the axes rectangle
            W, H = a.size()
            x, y, w, h = a.position
            panel = a.panel()
            self.assertAlmostEqual(panel[0], x * W, places=2, msg=vid)
            self.assertAlmostEqual(panel[1], (1 - y - h) * H, places=2, msg=vid)
            self.assertAlmostEqual(panel[2], w * W, places=2, msg=vid)
            self.assertAlmostEqual(panel[3], h * H, places=2, msg=vid)
            for pid in PRODUCTS:
                self.assertEqual(HS.land_hex(pid), "#ffffff", pid)
            if vid in POINTS and not crosses_dateline(v):
                name, lat, lon = POINTS[vid]
                x1, y1 = a.pixel(lon, lat)
                x2, y2 = b.pixel(lon, lat)
                self.assertLess(abs(x1 - x2) + abs(y1 - y2), 0.5, f"{vid} {name}")
                g = sample_grid(a, 8, 0.25)
                # the lookup cell at that pixel is the cell-center index, lon mod 360
                fi, fj = cell_ij(lat, lon)
                # nearest stride sample to the town pixel
                col = int(np.clip(round((x1 - g["px"]) / 8), 0, g["nx"] - 1))
                row = int(np.clip(round((y1 - g["py"]) / 8), 0, g["ny"] - 1))
                self.assertLess(abs(g["fi"][row, col] - fi), 1.0, f"{vid} {name} lat cell")
                self.assertLess(abs(g["fj"][row, col] - fj), 1.0, f"{vid} {name} lon cell")
            a.close(); b.close()

    def test_half_cell_edges_sit_outside_the_centers(self):
        edges = half_cell_edges([10.0, 10.25, 10.5])
        self.assertAlmostEqual(edges[0], 9.875)
        self.assertAlmostEqual(edges[1], 10.125)
        self.assertAlmostEqual(edges[-1], 10.625)
        fi, fj = cell_ij(21.3069, -157.8583)
        self.assertAlmostEqual(float(np.mod(-157.8583, 360.0)) / 0.25, float(fj))
        self.assertAlmostEqual((90.0 - 21.3069) / 0.25, float(fi))

    def test_wave_land_mask_hugs_the_coast(self):
        cases = [
            ("hiw", self.views["hiw"], ("Honolulu", 21.3069, -157.8583), HI_BUOY),
            ("bigi", self.views["bigi"], ("Hilo", 19.7297, -155.09), BIGI_OFFSHORE),
            ("wc", {"proj": ["merc", -134], "ll": [-152.0, -116.0, 31.8, 49.8]}, WC_TOWN, WC_BUOY),
        ]
        for vid, v, town, buoy in cases:
            self._one_mask(vid, v, town, buoy)

    def _grid(self, cam, land):
        px, py, pw, ph = cam.panel()
        corners = [cam.lonlat(px + 1, py + 1), cam.lonlat(px + pw - 1, py + 1),
                   cam.lonlat(px + 1, py + ph - 1), cam.lonlat(px + pw - 1, py + ph - 1)]
        lons = [c[0] for c in corners]
        lats = [c[1] for c in corners]
        i0 = int(np.floor((90.0 - max(lats) - 0.5) / 0.25))
        i1 = int(np.ceil((90.0 - min(lats) + 0.5) / 0.25))
        j0 = int(np.floor((min(lons) - 0.5) / 0.25))
        j1 = int(np.ceil((max(lons) + 0.5) / 0.25))
        ii = np.arange(i0, i1 + 1)
        jj = np.arange(j0, j1 + 1)
        lat_c = 90.0 - ii * 0.25
        lon_c = np.mod(jj * 0.25, 360.0)
        lon_f = np.where(lon_c > 180.0, lon_c - 360.0, lon_c)
        from shapely.geometry import Point
        mask = np.ones((len(ii), len(jj)))
        for a, lat in enumerate(lat_c):
            for b, lon in enumerate(lon_f):
                if land.contains(Point(float(lon), float(lat))):
                    mask[a, b] = np.nan
        lat_e, lon_e = half_cell_edges(lat_c), half_cell_edges(lon_f)
        if lat_e[0] > lat_e[-1]:
            lat_e, mask = lat_e[::-1], mask[::-1, :]
        if lon_e[0] > lon_e[-1]:
            lon_e, mask = lon_e[::-1], mask[:, ::-1]
        return lon_e, lat_e, mask

    def _draw(self, cam, mesh, polygon):
        from matplotlib.colors import ListedColormap
        import cartopy.feature as cf
        cam.ax.set_facecolor("#000000")
        cam.fig.patch.set_facecolor("#000000")
        if mesh:
            lon_e, lat_e, mask = mesh
            cam.ax.pcolormesh(lon_e, lat_e, np.ma.masked_invalid(mask), cmap=ListedColormap(["#1a6ea8"]),
                              transform=ccrs.PlateCarree(), zorder=2)
        if polygon:
            cam.ax.add_feature(cf.GSHHSFeature(scale="full", levels=[1]),
                               facecolor="#ffffff", edgecolor="none", zorder=3)
        cam.snap()
        cam.fig.canvas.draw()
        self.assertAlmostEqual(cam.ax.get_xlim()[0], cam.xlim[0], places=3)
        self.assertAlmostEqual(cam.ax.get_xlim()[1], cam.xlim[1], places=3)
        self.assertAlmostEqual(cam.ax.get_ylim()[0], cam.ylim[0], places=3)
        self.assertAlmostEqual(cam.ax.get_ylim()[1], cam.ylim[1], places=3)
        W, H = [int(round(s)) for s in cam.size()]
        return np.frombuffer(cam.fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(H, W, 4).copy()

    def _one_mask(self, vid, v, town, buoy):
        cam = Camera(view_dict(v))
        px, py, pw, ph = cam.panel()
        # land polygons for the pinned window, not just the seed box
        corners = [cam.lonlat(px, py), cam.lonlat(px + pw, py), cam.lonlat(px, py + ph), cam.lonlat(px + pw, py + ph)]
        folds = [lon - 360.0 if lon > 180.0 else lon for lon, _lat in corners]
        lats = [lat for _lon, lat in corners]
        land = land_geometry(min(folds), max(folds), min(lats), max(lats))
        grid = self._grid(cam, land)
        mesh = self._draw(cam, grid, polygon=False)
        # same camera bounds on the land-fill layer
        filled = Camera(view_dict(v))
        poly = self._draw(filled, None, polygon=True)
        self.assertEqual(filled.size(), cam.size(), vid)
        for i in range(4):
            self.assertAlmostEqual(filled.bounds()[i], cam.bounds()[i], places=3, msg=f"{vid} layer bounds")
            self.assertAlmostEqual(filled.panel()[i], cam.panel()[i], places=2, msg=f"{vid} layer panel")
        # data reaches the panel (no inner rectangle). West edge of these views is ocean.
        west = mesh[int(py + ph / 2), int(px + 4), :3]
        self.assertGreater(int(west[2]), 80, f"{vid} data inset from the panel {west.tolist()}")
        name, lat, lon = town
        self.assertTrue(self._white(poly, filled, lat, lon), f"{vid} {name} is not on the white land fill")
        bname, blat, blon = buoy
        self.assertGreater(self._blue(mesh, cam, blat, blon), 0.5, f"{vid} {bname} is not on the ocean")
        self.assertFalse(self._white(poly, filled, blat, blon), f"{vid} {bname} sits on land")
        self._coast_hugs(mesh, poly, cam, vid)
        cam.close()
        filled.close()

    def _at(self, buf, cam, lat, lon):
        x, y = cam.pixel(lon, lat)
        return buf[int(round(y)), int(round(x)), :3].astype(int)

    def _white(self, buf, cam, lat, lon):
        p = self._at(buf, cam, lat, lon)
        return int(p.min()) > 200

    def _blue(self, buf, cam, lat, lon):
        p = self._at(buf, cam, lat, lon)
        return int(p[2]) > 80 and int(p[2]) > int(p[0]) + 30

    def _coast_hugs(self, mesh, poly, cam, vid):
        """NaN land-mask edge stays within half a cell of the GSHHG fill."""
        m = mesh[:, :, :3].astype(int)
        p = poly[:, :, :3].astype(int)
        ocean = (m[:, :, 2] > 80) & (m[:, :, 2] > m[:, :, 0] + 30)
        hole = m.max(axis=2) < 40
        edge = np.zeros(hole.shape, dtype=bool)
        edge[1:, :] |= hole[1:, :] & ocean[:-1, :]
        edge[:-1, :] |= hole[:-1, :] & ocean[1:, :]
        edge[:, 1:] |= hole[:, 1:] & ocean[:, :-1]
        edge[:, :-1] |= hole[:, :-1] & ocean[:, 1:]
        white = p.min(axis=2) > 220
        shore = np.zeros(white.shape, dtype=bool)
        shore[1:, :] |= white[1:, :] & ~white[:-1, :]
        shore[:-1, :] |= white[:-1, :] & ~white[1:, :]
        shore[:, 1:] |= white[:, 1:] & ~white[:, :-1]
        shore[:, :-1] |= white[:, :-1] & ~white[:, 1:]
        px, py, pw, ph = [int(round(v)) for v in cam.panel()]
        inside = np.zeros(edge.shape, dtype=bool)
        mrg = 8
        inside[py + mrg:py + ph - mrg, px + mrg:px + pw - mrg] = True
        edge &= inside
        shore &= inside
        ys, xs = np.where(edge)
        cys, cxs = np.where(shore)
        self.assertGreater(len(xs), 20, vid)
        self.assertGreater(len(cxs), 20, vid)
        x0, y0 = cam.pixel(-157.8, 21.0)
        x1, y1 = cam.pixel(-157.8, 22.0)
        if abs(y1 - y0) < 1:
            x0, y0 = cam.pixel(-122.4, 37.5)
            x1, y1 = cam.pixel(-122.4, 38.5)
        half = 0.5 * 0.25 * abs(y1 - y0) + 3.0
        take = np.linspace(0, len(xs) - 1, num=min(250, len(xs)), dtype=int)
        far = 0
        for k in take:
            d2 = np.min((cxs - xs[k]) ** 2 + (cys - ys[k]) ** 2)
            if d2 > half * half:
                far += 1
        self.assertLess(far / len(take), 0.1, f"{vid} mask edge is more than half a cell from the GSHHG shore")


if __name__ == "__main__":
    unittest.main()
