#!/usr/bin/env python3
"""Ship land, coast and town layers for the views whose live R2 copies went stale.

The browser samples these views from this same camera (cameras.js), so a stale
Lambert lookup in R2 cannot draw the field as a parallelogram. Header chrome is
not drawn into the PNGs.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf

import camera as CAM
import house_style as HS
import fast_encode as FE

VIEWS = ("hiw", "bigi", "pnwhr", "pnwwide", "wa", "orco", "capasses", "passes", "socal", "cenca", "norca", "bay")
REG = json.load(open(os.path.join(ROOT, "regions", "regions.json")))
STATIONS = json.load(open(os.path.join(ROOT, "regions", "stations.json")))["stations"]
OUT = os.path.join(HERE, "site", "cam")
ASSET = "20261107warp"


def proj_of(p):
    if p[0] == "merc":
        return ccrs.Mercator(central_longitude=p[1])
    return ccrs.LambertConformal(central_longitude=p[1], central_latitude=p[2], standard_parallels=tuple(p[3]))


def view_dict(vid):
    # pnwhr150 is the 150 mi frame (globals and NBM). pnwhr is the hi-res CONUS frame.
    key = "pnwhr" if vid == "pnwhr150" else vid
    v = dict(REG["views"][key])
    if vid == "pnwhr" and v.get("hires"):
        v.update(v["hires"])
    v.pop("hires", None)
    v["proj"] = proj_of(v["proj"])
    if "ll" in v:
        v["ll"] = tuple(v["ll"])
    if "extent" in v:
        v["extent"] = tuple(v["extent"])
    return v


def new_fig(vid):
    fig, ax, _ky = None, None, None
    cam = CAM.Camera(view_dict(vid))
    fig, ax = cam.fig, cam.ax
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.patches.clear()
    HS.frame(ax)
    return cam


def save(cam, path):
    cam.snap()
    HS.frame(cam.ax)
    cam.fig.savefig(path, dpi=100, transparent=True)
    plt.close(cam.fig)


def town_list(cam):
    px, py, pw, ph = cam.panel()
    out = []
    seen = set()
    for t in STATIONS:
        if t.get("kind") != "town" or t["name"] in seen:
            continue
        x, y = cam.pixel(t["lon"], t["lat"])
        if px + 12 <= x <= px + pw - 12 and py + 12 <= y <= py + ph - 12:
            seen.add(t["name"])
            out.append({"n": t["name"], "la": round(t["lat"], 5), "lo": round(t["lon"], 5), "t": HS.town_tier(t["name"])})
    out.sort(key=lambda t: t["t"])
    return out


def grid(cam):
    px, py, pw, ph = cam.panel()
    nx, ny = 73, 37
    xs = np.linspace(px, px + pw, nx)
    ys = np.linspace(py, py + ph, ny)
    lon = np.empty((ny, nx))
    lat = np.empty((ny, nx))
    ang = np.empty((ny, nx))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            lo, la = cam.lonlat(x, y)
            if lo > 180:
                lo -= 360
            lon[j, i] = lo
            lat[j, i] = la
            x2, y2 = cam.pixel(lo, min(la + 0.05, 89))
            ang[j, i] = np.arctan2(-(y2 - y), x2 - x)
    return nx, ny, lon, lat, ang


def main():
    os.makedirs(OUT, exist_ok=True)
    HS.use_for_plots()
    only = os.environ.get("WX_CAM_ONLY", "").strip()
    views = [only] if only else list(VIEWS)
    cams = {}
    for vid in views:
        print("land", vid, flush=True)
        cam = new_fig(vid)
        HS.land(cam.ax, cf)
        HS.frame(cam.ax)
        save(cam, os.path.join(OUT, f"land_{vid}.png"))
        print("base", vid, flush=True)
        cam = new_fig(vid)
        HS.outlines(cam.ax, cf)
        if vid == "capasses":
            FE.major_roads(cam.ax)
        HS.frame(cam.ax)
        save(cam, os.path.join(OUT, f"base_{vid}.png"))
        print("grid", vid, flush=True)
        cam = new_fig(vid)
        towns = town_list(cam)
        nx, ny, lon, lat, ang = grid(cam)
        cams[vid] = (list(cam.panel()), nx, ny, lon, lat, ang, towns)
        plt.close(cam.fig)
    spec = {"v": ASSET, "views": {}}
    if only:
        prev = open(os.path.join(HERE, "site", "cameras.js"), encoding="utf-8").read()
        spec = json.loads(prev[len("window.WXCAM = "):-2])
    for vid, (panel, nx, ny, lon, lat, ang, towns) in cams.items():
        label_key = "pnwhr" if vid == "pnwhr150" else vid
        entry = {
            "label": REG["views"][label_key]["label"],
            "fig": [1920, 1080],
            "panel": [round(float(v), 2) for v in panel],
            "nx": nx, "ny": ny,
            "lon": [round(float(v), 4) for v in lon.ravel()],
            "lat": [round(float(v), 4) for v in lat.ravel()],
            "ang": [round(float(v), 5) for v in ang.ravel()],
            "towns": towns,
        }
        if vid == "pnwhr150":
            entry["stem"] = "pnwhr150"
        spec["views"][vid] = entry
    js = "window.WXCAM = " + json.dumps(spec, separators=(",", ":")) + ";\n"
    open(os.path.join(HERE, "site", "cameras.js"), "w").write(js)
    print("wrote cameras.js", len(js), flush=True)


if __name__ == "__main__":
    main()
