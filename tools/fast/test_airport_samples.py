"""Town readouts sample official airports, and the same town matches across views."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np

import temp_maps as TM
from test_pnwwide_crop import hrrr_ij, nbm_ij

# Downtown / gazetteer pins that used to be sampled on some views, vs the airport.
LABEL_VARIANTS = {
    "Seattle": [(47.61, -122.33), (47.6062, -122.3321), (47.6, -122.315)],
    "Spokane": [(47.66, -117.43), (47.6588, -117.4260)],
    "Portland": [(45.52, -122.68), (45.5152, -122.6784)],
    "Yakima": [(46.60, -120.51), (46.6021, -120.5059)],
    "Wenatchee": [(47.42, -120.31), (47.4235, -120.3103)],
    "Bellingham": [(48.75, -122.48), (48.7519, -122.4787)],
    "Olympia": [(47.04, -122.90), (47.0379, -122.9007)],
    "Redding": [(40.5865, -122.3917), (40.5865, -122.3917)],
    "Sacramento": [(38.5816, -121.4944), (38.5816, -121.4944)],
}

NBM_CROP_PREVIEW = [326, 1524, 0, 1289]
HRRR_CROP = [216, 1139, -277, 973]
GFS_CROP = [8, 367, 484, 1421]


def gfs_ij(lat, lon, crop=GFS_CROP, res=0.25):
    return (90.0 - lat) / res - crop[0], ((lon % 360.0) / res) - crop[2]


def rounded_lcc(to_ij, lat, lon, crop):
    fi, fj = to_ij(lon, lat)
    return float(round(fi - crop[0])), float(round(fj - crop[2]))


class AirportSamples(unittest.TestCase):
    def test_seattle_samples_seatac_ksea(self):
        pin = TM.sample_pin("Seattle", 47.61, -122.33)
        info = TM.sample_airport("Seattle", 47.61, -122.33)
        self.assertIsNotNone(info)
        self.assertEqual(info["icao"], "KSEA")
        self.assertAlmostEqual(pin[0], 47.44472, places=4)
        self.assertAlmostEqual(pin[1], -122.31361, places=4)
        self.assertLess(TM.airport_km(pin[0], pin[1], 47.449, -122.309), 2.0)

    def test_same_town_same_pin_from_different_label_coords(self):
        for name, coords in LABEL_VARIANTS.items():
            pins = [TM.sample_pin(name, la, lo) for la, lo in coords]
            unique = {(round(p[0], 5), round(p[1], 5)) for p in pins}
            self.assertEqual(len(unique), 1, f"{name} pins {pins}")
            icaos = {TM.sample_airport(name, la, lo)["icao"] for la, lo in coords}
            self.assertEqual(len(icaos), 1, f"{name} icaos {icaos}")

    def test_vancouver_wa_and_bc_use_different_airports(self):
        wa = TM.sample_airport("Vancouver", 45.64, -122.66)
        bc = TM.sample_airport("Vancouver", 49.25, -123.12)
        self.assertIsNotNone(wa)
        self.assertIsNotNone(bc)
        self.assertEqual(wa["icao"], "KVUO")
        self.assertEqual(bc["icao"], "CYVR")

    def test_long_beach_wa_is_not_klgb(self):
        wa = TM.sample_airport("Long Beach", 46.35, -124.05)
        self.assertIsNone(wa)
        pin = TM.sample_pin("Long Beach", 46.35, -124.05)
        self.assertAlmostEqual(pin[0], 46.35, places=3)
        self.assertAlmostEqual(pin[1], -124.05, places=3)
        ca = TM.sample_airport("Long Beach", 33.77, -118.19)
        self.assertIsNotNone(ca)
        self.assertEqual(ca["icao"], "KLGB")

    def test_cross_view_native_grid_indices_match(self):
        """Same airport pin -> same nearest native cell on NBM, HRRR and GFS, for every label variant."""
        to_n, to_h = nbm_ij(), hrrr_ij()
        for name, coords in LABEL_VARIANTS.items():
            nbm, hrrr, gfs = set(), set(), set()
            for la, lo in coords:
                pla, plo = TM.sample_pin(name, la, lo)
                nbm.add(rounded_lcc(to_n, pla, plo, NBM_CROP_PREVIEW))
                hrrr.add(rounded_lcc(to_h, pla, plo, HRRR_CROP))
                gi, gj = gfs_ij(pla, plo)
                gfs.add((round(gi, 5), round(gj, 5)))
            self.assertEqual(len(nbm), 1, f"{name} nbm {nbm}")
            self.assertEqual(len(hrrr), 1, f"{name} hrrr {hrrr}")
            self.assertEqual(len(gfs), 1, f"{name} gfs {gfs}")

    def test_passes_are_not_in_the_airport_table(self):
        for full, (label, la, lo, _el) in TM.WA_PASSES.items():
            self.assertIsNone(TM.sample_airport(full, la, lo))
            self.assertIsNone(TM.sample_airport(label, la, lo))
            pin = TM.sample_pin(label, la, lo)
            self.assertEqual(pin, (la, lo))

    def test_wa_and_wide_views_read_seattle_at_the_same_airport(self):
        import cartopy.crs as ccrs
        import matplotlib.pyplot as plt
        import regions

        regions.apply(TM, ccrs)
        lats = np.linspace(32.0, 51.0, 191)
        lons = np.linspace(-125.0, -114.0, 221)
        field = (lats, lons, np.broadcast_to(lats[:, None], (len(lats), len(lons))).copy())
        got = {}
        for vid in ("wa", "pnwwide", "pnw", "pnwhr"):
            fig, ax, _ = TM.frame(vid)
            try:
                TM.towns(ax, vid, field, TM.fmt_int)
                vals = getattr(ax, "town_values", {}) or {}
                self.assertIn("Seattle", vals, f"Seattle missing on {vid}")
                got[vid] = vals["Seattle"]
            finally:
                plt.close(fig)
        # The sampled field is latitude, so the stored value is the sample-point latitude.
        for vid, v in got.items():
            self.assertAlmostEqual(v, 47.44472, places=3, msg=f"{vid} Seattle={v}")
        self.assertEqual(len({round(v, 4) for v in got.values()}), 1, got)

        # The Washington-list path (used by Cascade Passes / encode after popping REGION_TOWNS["wa"])
        # must hit the same pin.
        keep = TM.REGION_TOWNS.pop("wa", None)
        try:
            fig, ax, _ = TM.frame("wa")
            try:
                TM.towns(ax, "wa", field, TM.fmt_int)
                vals = getattr(ax, "town_values", {}) or {}
                self.assertIn("Seattle", vals)
                self.assertAlmostEqual(vals["Seattle"], 47.44472, places=3)
            finally:
                plt.close(fig)
        finally:
            if keep is not None:
                TM.REGION_TOWNS["wa"] = keep


if __name__ == "__main__":
    unittest.main()
