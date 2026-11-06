"""1920x1080 map chrome: color key above the map, timestamp band below, map at its true aspect."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import house_style as HS


class ScreenLayout(unittest.TestCase):
    def test_figure_is_16_by_9(self):
        w, h = HS.SCREEN_IN
        self.assertEqual(HS.SCREEN_PX, (1920, 1080))
        self.assertAlmostEqual(w / h, 16 / 9, places=5)
        self.assertEqual((int(w * 100), int(h * 100)), (1920, 1080))

    def test_key_is_above_the_map_and_stamp_is_below(self):
        class Fig:
            def get_size_inches(self):
                return HS.SCREEN_IN
        # wide Oregon coast and tall California passes both keep their aspect inside the frame
        for aspect in (HS.geo_aspect((-132.5, -121.3, 41.95, 46.35)), HS.geo_aspect((-123.0, -117.4, 34.4, 41.75))):
            lay = HS.screen_layout(Fig(), aspect)
            left, bottom, mw, mh = lay["axes"]
            map_top = bottom + mh
            self.assertGreater(lay["key_y"], map_top)          # color bar sits above the map
            self.assertGreater(bottom, lay["stamp_y"])         # map sits above the timestamp
            got = (mw * HS.SCREEN_IN[0]) / (mh * HS.SCREEN_IN[1])
            self.assertAlmostEqual(got, aspect, places=2)      # axes hug the geography (no stretch)
            self.assertGreaterEqual(left, 0.01)
            self.assertLessEqual(left + mw, 0.99)

    def test_oregon_coast_and_california_passes_extents_unchanged(self):
        import json
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))
        with open(p) as f:
            R = json.load(f)
        self.assertEqual(R["views"]["orco"]["ll"], [-132.5, -121.3, 41.95, 46.35])
        self.assertEqual(R["views"]["capasses"]["ll"], [-123.0, -117.4, 34.4, 41.75])
        self.assertEqual(R["views"]["capasses"]["label"], "California Passes")


if __name__ == "__main__":
    unittest.main()
