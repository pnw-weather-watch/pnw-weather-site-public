"""Menus list a product only when that model encodes its fields.

GFS, IFS and AIFS used to offer refc / snow / ir / frz / vis / gust products whose getters
raise or whose open files never contain the field. Selecting one fell back to another
product. publish_static rebuilds manifest.json from the product table, so the only=
lists (PRODUCT_ONLY) are what keep the prune.
"""
import inspect
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_encode as fe

# Still no source field, so the menu must not offer them (selecting one used to fall back to another product).
ABSENT = {
    "gfs": (),
    "ifs": ("refc", "vis", "ir"),
    "aifs": ("gust10", "gust3", "gust6", "gust12", "gust24", "refc", "vis", "ir"),
}
# Encoded directly, or derived from fields the open files publish. NBM's menu is gust10. ifs9 is IFS.
PRESENT = {
    "hrrr": ("refc", "snow", "frz", "snowlvl", "vis", "ir", "gust10", "gust3", "gust6", "gust12", "gust24"),
    "rrfs": ("refc", "snow", "frz", "snowlvl", "vis", "ir", "gust10", "gust6"),
    "rrfsna": ("refc", "snow", "frz", "snowlvl", "vis", "ir", "gust10", "gust6"),
    "gfs": ("refc", "snow", "ir", "frz", "snowlvl", "vis", "gust10", "gust3", "gust6", "gust12", "gust24"),
    "ifs": ("snow", "frz", "snowlvl", "gust10", "gust3", "gust6", "gust12", "gust24"),
    "aifs": ("snow", "frz", "snowlvl"),
    "ifs9": ("snow", "frz", "snowlvl", "gust10", "gust12"),
    "nbm": ("gust10",),
}


def published(prods, model):
    """Same membership rule static() uses after stamp_product_only."""
    fe.stamp_product_only(prods)
    return {k for k, v in prods.items() if fe.menu_keeps(k, v, model)}


class MenuProducts(unittest.TestCase):
    def test_absent_products_are_not_offered(self):
        for model, pids in ABSENT.items():
            for pid in pids:
                self.assertNotIn(fe.as_model(model), fe.PRODUCT_ONLY[pid], (model, pid))
                self.assertFalse(fe.menu_keeps(pid, {}, model), (model, pid))

    def test_encoded_products_stay(self):
        for model, pids in PRESENT.items():
            for pid in pids:
                self.assertIn(fe.as_model(model), fe.PRODUCT_ONLY[pid], (model, pid))
                self.assertTrue(fe.menu_keeps(pid, {}, model), (model, pid))

    def test_unrestricted_product_stays_on_every_model(self):
        for model in ("gfs", "ifs", "aifs", "hrrr", "nbm"):
            self.assertTrue(fe.menu_keeps("t2m", {}, model))

    def test_stamp_overrides_a_copied_aifs_gust(self):
        # gust12/24 are dict copies of gust6. A stale only= that still names AIFS must not survive the stamp.
        prods = {"gust12": {"only": ("hrrr", "rrfs", "gfs", "ifs", "aifs")}, "t2m": {}}
        kept = published(prods, "aifs")
        self.assertNotIn("gust12", kept)
        self.assertIn("t2m", kept)
        self.assertEqual(prods["gust12"]["only"], fe.PRODUCT_ONLY["gust12"])

    def test_publish_filter_matches_the_live_fail_set(self):
        prods = {pid: {} for pid in fe.PRODUCT_ONLY}
        prods["t2m"] = {}
        for model, banned in ABSENT.items():
            kept = published({k: dict(v) for k, v in prods.items()}, model)
            for pid in banned:
                self.assertNotIn(pid, kept, (model, pid))
            self.assertIn("t2m", kept)
        hrrr = published({k: dict(v) for k, v in prods.items()}, "hrrr")
        for pid in PRESENT["hrrr"]:
            self.assertIn(pid, hrrr)

    def test_static_stamps_before_the_menu_filter(self):
        src = inspect.getsource(fe.static)
        stamp = src.index("stamp_product_only(prods)")
        keep = src.index("menu_keeps(k, v, m)")
        self.assertLess(stamp, keep)


if __name__ == "__main__":
    unittest.main()
