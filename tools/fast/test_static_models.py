"""The static lookup that crashed HRRR must succeed for every model.

HRRR, RRFS and NBM are Lambert grids. Their lookup used to pass a 1-row x
and a 1-column y into cartopy, which raises 'x and y arrays must have the
same length'. Every model now samples through camera.sample_grid, the same
call static() makes. This does not download GRIB or draw the color keys.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import cartopy.crs as ccrs
import matplotlib
matplotlib.use("Agg")
import numpy as np

import camera as CAM
import fast_encode as FE

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
REGIONS = json.load(open(os.path.join(ROOT, "regions", "regions.json")))


def proj_of(p):
    if p[0] == "merc":
        return ccrs.Mercator(central_longitude=p[1])
    return ccrs.LambertConformal(central_longitude=p[1], central_latitude=p[2], standard_parallels=tuple(p[3]))


def view_dict(vid):
    v = dict(REGIONS["views"][vid])
    v["proj"] = proj_of(v["proj"])
    if "ll" in v:
        v["ll"] = tuple(v["ll"])
    if "extent" in v:
        v["extent"] = tuple(v["extent"])
    return v


def lambert_to_ij(model):
    """Same Lambert transform static() uses, without a downloaded grid origin."""
    md = FE.MODELS[model]
    spec = md.get("lcc", FE.HRRR_LCC)
    rad = md.get("radius", 6371229.0)
    globe = ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad)
    hp = ccrs.LambertConformal(globe=globe, **spec)
    pc = ccrs.PlateCarree()

    def to_ij(lon, lat):
        folded = np.where(np.asarray(lon) > 180.0, np.asarray(lon) - 360.0, lon)
        hh = hp.transform_points(pc, folded, lat)
        if hh.shape[:-1] != np.shape(lon):
            raise ValueError("x and y arrays must have the same length")
        return hh[..., 1], hh[..., 0]

    return to_ij


class StaticModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cams = {}
        for vid in REGIONS["views"]:
            cls.cams[vid] = CAM.Camera(view_dict(vid))

    @classmethod
    def tearDownClass(cls):
        for cam in cls.cams.values():
            cam.close()

    def test_static_lookup_for_every_model(self):
        listed = set(REGIONS["model_views"])
        self.assertTrue({"hrrr", "rrfs", "nbm"} <= listed)
        for model, views in REGIONS["model_views"].items():
            self.assertIn(model, FE.MODELS, model)
            md = FE.MODELS[model]
            to_ij = lambert_to_ij(model) if md["grid"] == "lcc" else None
            res = md.get("res", 0.25)
            for vid in views:
                g = CAM.sample_grid(self.cams[vid], FE.STRIDE, res, to_ij=to_ij)
                self.assertEqual(g["fi"].shape, g["fj"].shape, f"{model} {vid}")
                self.assertEqual(g["fi"].shape, g["ang"].shape, f"{model} {vid}")
                self.assertGreater(g["fi"].shape[0], 1, vid)
                self.assertGreater(g["fi"].shape[1], 1, vid)
                self.assertTrue(np.isfinite(g["lat"]).any(), f"{model} {vid}")
                self.assertTrue(np.isfinite(g["lon"]).any(), f"{model} {vid}")

    def test_hrrr_windows_fill_the_rectangle(self):
        """pnwhr, Oregon & Coast and California Passes stay inside the HRRR grid.

        A window that crosses the domain edge is what drew the diagonal wedge.
        """
        rad = 6371229.0
        globe = ccrs.Globe(ellipse="sphere", semimajor_axis=rad, semiminor_axis=rad)
        hp = ccrs.LambertConformal(globe=globe, **FE.HRRR_LCC)
        pc = ccrs.PlateCarree()
        sw = hp.transform_point(-122.719528, 21.138123, pc)
        gx0, gy0, dx = sw[0], sw[1], 3000.0
        ny, nx = 1059, 1799

        def to_ij(lon, lat):
            folded = np.where(np.asarray(lon) > 180.0, np.asarray(lon) - 360.0, lon)
            hh = hp.transform_points(pc, folded, lat)
            return (hh[..., 1] - gy0) / dx, (hh[..., 0] - gx0) / dx

        for vid in ("pnwhr", "orco", "capasses"):
            g = CAM.sample_grid(self.cams[vid], FE.STRIDE, 3.0, to_ij=to_ij)
            fi, fj = g["fi"], g["fj"]
            ok = np.isfinite(fi) & np.isfinite(fj) & (fi >= 0) & (fi <= ny - 1) & (fj >= 0) & (fj <= nx - 1)
            self.assertGreater(float(ok.mean()), 0.98, vid)

    def test_static_source_uses_one_mesh_for_lambert(self):
        with open(os.path.join(os.path.dirname(__file__), "fast_encode.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('to_ij=to_ij if MD["grid"] == "lcc" else None', src)
        self.assertNotIn("gxp[None, :] / pw) * (x1 - x0); PY", src)


if __name__ == "__main__":
    unittest.main()
