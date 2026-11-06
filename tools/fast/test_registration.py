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


def open_view(v):
    fig = plt.figure(figsize=HS.SCREEN_IN, dpi=100)
    lay = HS.screen_layout(fig)
    ax = fig.add_axes(lay["axes"], projection=proj_of(v["proj"]))
    if "extent" in v:
        ax.set_extent(v["extent"], crs=ax.projection)
    else:
        ax.set_extent(v["ll"], crs=ccrs.PlateCarree())
    HS.fill_projected_limits(ax, lay["axes"])
    ax.apply_aspect()
    fig.canvas.draw()
    HS.fill_projected_limits(ax, lay["axes"])
    fig.canvas.draw()
    return fig, ax, lay


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


if __name__ == "__main__":
    unittest.main()
