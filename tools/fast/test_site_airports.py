"""The site itself reads town numbers at the official airport: catalog slots (encoder / runner /
auto-promote), view_fixes overrides, and the viewer's own camera-view labels (selection.js townPoint).
Seattle must read the KSEA grid point on the Pacific NW, Washington and wide views."""
import copy
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import town_airports as TA

KSEA = (47.44472, -122.31361)
DOWNTOWN = (47.6062, -122.3321)
LIVE_NBM = [326, 1524, -210, 1289]
HRRR = [216, 1139, -277, 973]
GFS = [8, 367, 484, 1421]
IFS9 = [310, 749, 1905, 2651]
RRFSNA = [0, 683, 0, 1127]
VIEWS = ("pnw", "wa", "pnwwide")


def gfs_slot(lat, lon):
    return round((90 - lat) / 0.25 - GFS[0], 5), round((lon % 360) / 0.25 - GFS[2], 5)


def fixture():
    """Seattle at the downtown label point on every view (the pre-11-11 state), plus Vancouver WA/BC."""
    def town(name, ij, x=0.4, y=0.5):
        return dict(name=name, kind="town", x=x, y=y, fi=ij[0], fj=ij[1], size=12, color="#000")
    models = {}
    for m, crop, grid, res in (("gfs", GFS, "ll", "0.25°"), ("epsm", GFS, "ll", "0.5° · single member"),
                               ("ifs9", IFS9, "ll", "9 km (0.1°)"), ("hrrr", HRRR, "lcc", "3 km"),
                               ("nbm", LIVE_NBM, "lcc", "2.5 km"), ("rrfsna", RRFSNA, "rotll", "13 km")):
        md = dict(grid=grid, res=res, crop=list(crop))
        down = TA.grid_ij(m, md, *DOWNTOWN)
        md["views"] = {v: {"towns": [town("Seattle", down), dict(name="Snoqualmie", kind="pass", x=.5, y=.5, fi=1.0, fj=2.0)]} for v in VIEWS}
        models[m] = md
    models["gfs"]["views"]["wa"]["towns"].append(town("Vancouver", gfs_slot(45.63, -122.67)))
    models["gfs"]["views"]["pnw"]["towns"].append(town("Vancouver", gfs_slot(49.26, -123.12)))
    return {"models": models, "runs": {}}


class SiteAirports(unittest.TestCase):
    def test_seattle_reads_ksea_on_pnw_wa_and_wide_views_every_model(self):
        man = fixture()
        before_xy = {(m, v): [(t["x"], t["y"]) for t in V["towns"]] for m, md in man["models"].items() for v, V in md["views"].items()}
        TA.apply(man)
        for m, md in man["models"].items():
            want = TA.grid_ij(m, md, *KSEA)
            for v in VIEWS:
                sea = next(t for t in md["views"][v]["towns"] if t["name"] == "Seattle")
                self.assertEqual((sea["fi"], sea["fj"]), want, f"{m} {v}")
                self.assertEqual(sea["ap"], "KSEA")
                self.assertEqual([(t["x"], t["y"]) for t in md["views"][v]["towns"]], before_xy[(m, v)], "labels must not move")
            pas = next(t for t in md["views"]["wa"]["towns"] if t["kind"] == "pass")
            self.assertEqual((pas["fi"], pas["fj"]), (1.0, 2.0), "passes keep their own point")
        # known grid points (live crops)
        self.assertEqual(TA.grid_ij("nbm", man["models"]["nbm"], *KSEA), (877.0, 624.0))
        self.assertEqual(TA.grid_ij("hrrr", man["models"]["hrrr"], *KSEA), (730.0, 554.0))
        self.assertEqual(TA.grid_ij("rrfsna", man["models"]["rrfsna"], *KSEA), (275.0, 505.0))

    def test_member_viewers_use_the_parent_quarter_degree_grid(self):
        man = fixture(); TA.apply(man)
        e = next(t for t in man["models"]["epsm"]["views"]["wa"]["towns"] if t["name"] == "Seattle")
        g = next(t for t in man["models"]["gfs"]["views"]["wa"]["towns"] if t["name"] == "Seattle")
        self.assertEqual((e["fi"], e["fj"]), (g["fi"], g["fj"]))
        self.assertGreater(e["fj"], 0)

    def test_same_name_towns_pick_the_airport_near_their_label(self):
        man = fixture(); TA.apply(man)
        wa = next(t for t in man["models"]["gfs"]["views"]["wa"]["towns"] if t["name"] == "Vancouver")
        bc = next(t for t in man["models"]["gfs"]["views"]["pnw"]["towns"] if t["name"] == "Vancouver")
        self.assertEqual((wa["ap"], bc["ap"]), ("KVUO", "CYVR"))

    def test_idempotent_and_runner_and_promote_hooks(self):
        man = fixture(); TA.apply(man); snap = copy.deepcopy(man)
        self.assertEqual(TA.apply(man), 0)
        self.assertEqual(man, snap)
        import auto_promote_live as AP
        man2 = fixture()
        AP.apply_manifest(man2, {}, "nbm", "2026111112", {"complete": True, "steps": [{"f": 1}]}, 2)
        sea = next(t for t in man2["models"]["nbm"]["views"]["wa"]["towns"] if t["name"] == "Seattle")
        self.assertEqual((sea["fi"], sea["fj"]), (877.0, 624.0))
        with open(os.path.join(HERE, "fast_cycle.py")) as f: src = f.read()
        self.assertIn("TA.apply(mn, [m])", src)
        for fn, needle in (("fast_encode.py", "TA.apply(man, [m])"), ("view_fixes.py", "TA.apply_view_fixes(doc, man)")):
            with open(os.path.join(HERE, fn)) as f: self.assertIn(needle, f.read())

    def test_viewer_camera_labels_call_town_point(self):
        with open(os.path.join(HERE, "site", "viewer.js")) as f: v = f.read()
        body = v[v.index("function drawCamLabels"):]
        body = body[:body.index("\nfunction ")]
        self.assertIn("WXSelect.townPoint(model, V.towns, S._ap, name, lat, lon)", body)
        self.assertIn("valueAt(t.la, t.lo, t.n)", body)
        self.assertIn('static/town_airports.json', v)

    def test_view_fixes_overrides_follow_the_airport(self):
        man = fixture()
        fx = {"models": {"gfs": {"pnwt": {"towns_png": "static/towns_pnwt_v2.png",
              "towns": [dict(name="Seattle", kind="town", x=.4, y=.5, fi=gfs_slot(*DOWNTOWN)[0], fj=gfs_slot(*DOWNTOWN)[1])]}}}}
        TA.apply_view_fixes(fx, man)
        t = fx["models"]["gfs"]["pnwt"]["towns"][0]
        self.assertEqual((t["fi"], t["fj"]), gfs_slot(*KSEA))

    def test_benjamin_table_towns_present(self):
        T = TA.table()
        want = {"Renton": "KRNT", "Kelso": "KKLS", "Friday Harbor": "KFHR", "Pasco": "KPSC", "Spokane Valley": "KSFF",
                "Puyallup": "KPLU", "Corvallis": "KCVO", "The Dalles": "KDLS", "Hermiston": "KHRI", "Sandpoint": "KSZT",
                "Moscow": "KPUW", "Kamloops": "CYKA", "Comox": "CYQQ", "Winthrop": "KS52", "Grants Pass": "K3S8"}
        for n, icao in want.items():
            self.assertIn(icao, [s["icao"] for s in T.get(n, [])], n)
        self.assertEqual([(s["icao"], s["lat"], s["lon"]) for s in T["Oak Harbor"]], [("KOKH", 48.2515, -122.6737)])
        self.assertEqual(T["Port Townsend"][0].get("faa"), "0S9")
        # Oak Harbor matches Benjamin's table (KOKH); grid points on the live crops
        self.assertEqual(TA.grid_ij("nbm", {"grid": "lcc", "crop": LIVE_NBM}, 48.2515, -122.6737), (917.0, 620.0))
        self.assertEqual(TA.grid_ij("hrrr", {"grid": "lcc", "crop": HRRR}, 48.2515, -122.6737), (762.0, 553.0))
        self.assertEqual(TA.airport("Oak Harbor", 48.2934, -122.6432)["icao"], "KOKH")

    def test_viewer_camera_labels_read_the_same_point(self):
        """selection.js townPoint: catalog slot first, else the airport table, else the label; same index as Python."""
        man = fixture(); TA.apply(man)
        site = TA.site_table()
        cases = []
        for m in ("gfs", "hrrr", "nbm", "rrfsna", "ifs9"):
            md = man["models"][m]
            model = dict(id=m, grid=md["grid"], res=md["res"], crop=md["crop"])
            for v in VIEWS:
                cases.append(dict(m=m, v=v, model=model, slots=md["views"][v]["towns"], want=list(TA.grid_ij(m, md, *KSEA))))
        js = """
const S = require(%r); const site = %s; const cases = %s; const out = [];
for (const c of cases) {
  const a = S.townPoint(c.model, c.slots, site, "Seattle", 47.6062, -122.3321);
  const b = S.townPoint(c.model, [], site, "Seattle", 47.6062, -122.3321);   // no slot: viewer computes it
  out.push([c.m, c.v, [a.fi, a.fj], a.src, [b.fi, b.fj], b.src, b.icao, c.want]);
}
console.log(JSON.stringify(out));
""" % (os.path.join(HERE, "site", "selection.js"), json.dumps(site), json.dumps(cases))
        res = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
        for m, v, a, asrc, b, bsrc, icao, want in res:
            self.assertEqual(asrc, "slot")
            self.assertEqual(a, want, f"{m} {v} slot")
            self.assertEqual((bsrc, icao), ("airport", "KSEA"))
            if m in ("hrrr", "nbm", "rrfsna"):
                self.assertEqual(b, want, f"{m} {v} computed")
            else:
                self.assertAlmostEqual(b[0], want[0], places=3); self.assertAlmostEqual(b[1], want[1], places=3)


if __name__ == "__main__":
    unittest.main()
