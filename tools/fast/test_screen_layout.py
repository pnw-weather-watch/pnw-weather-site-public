"""1920x1080 map chrome: color key above the map, valid time under it, map at its true aspect."""
import datetime as dt
import os
import sys
import unittest
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forecast"))
import house_style as HS

PT = ZoneInfo("America/Los_Angeles")


def valid_line(when):
    vl = when.astimezone(PT)
    return f"Valid {vl:%a %-m-%-d} \u00b7 {vl:%-I %p} PT"


class ScreenLayout(unittest.TestCase):
    def test_figure_is_16_by_9(self):
        w, h = HS.SCREEN_IN
        self.assertEqual(HS.SCREEN_PX, (1920, 1080))
        self.assertAlmostEqual(w / h, 16 / 9, places=5)
        self.assertEqual((int(w * 100), int(h * 100)), (1920, 1080))

    def test_key_is_above_the_map_and_the_map_fills_the_slot(self):
        class Fig:
            def get_size_inches(self):
                return HS.SCREEN_IN
        lay = HS.screen_layout(Fig(), 1.2)
        left, bottom, mw, mh = lay["axes"]
        self.assertGreater(lay["key_y"], bottom + mh)
        self.assertGreater(bottom, lay["stamp_y"])
        self.assertAlmostEqual(left, 0.0, places=3)
        self.assertAlmostEqual(mw, 1.0, places=3)
        # a tall view and a wide view get the same full-bleed axes
        self.assertEqual(HS.screen_layout(Fig(), 0.4)["axes"], lay["axes"])

    def test_valid_line_is_pacific_wall_time(self):
        # 6 Nov 2026 22:00 UTC is 2 PM PST. 6 Jul 2026 21:00 UTC is 2 PM PDT.
        self.assertEqual(valid_line(dt.datetime(2026, 11, 6, 22, tzinfo=dt.timezone.utc)), "Valid Fri 11-6 \u00b7 2 PM PT")
        self.assertEqual(valid_line(dt.datetime(2026, 7, 6, 21, tzinfo=dt.timezone.utc)), "Valid Mon 7-6 \u00b7 2 PM PT")

    def test_view_frames_are_unchanged(self):
        import json
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "regions", "regions.json"))
        with open(p) as f:
            R = json.load(f)
        self.assertEqual(R["views"]["orco"]["ll"], [-132.5, -121.3, 41.95, 46.35])
        self.assertEqual(R["views"]["capasses"]["ll"], [-123.0, -117.4, 34.4, 41.75])
        self.assertEqual(R["views"]["hiw"]["ll"], [-168.0, -148.0, 16.08, 24.42])
        self.assertEqual(R["views"]["pnwhr"]["ll"], [-128.4, -112.6, 41.6, 50.4])


if __name__ == "__main__":
    unittest.main()
