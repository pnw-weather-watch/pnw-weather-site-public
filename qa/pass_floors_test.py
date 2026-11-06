"""Pass-chart floors live in one constant, matched in both pages.

Compared with the map refresh guard (qa/guard.py): that guard reloads the map and checks
the URL state. This check does not load a page. It locks the axis floors the pass
meteogram uses, which the refresh guard never reads.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "tools" / "fast" / "site" / "viewer.js"
METEO = ROOT / "tools" / "fast" / "site" / "meteograms.js"
WANT = {"passPrecipIn": 3, "passSnow6In": 12}


def floors(text, name):
    m = re.search(r"MG_FLOORS\s*=\s*(?:window\.MG_FLOORS\s*=\s*)?\{([^}]+)\}", text)
    if not m:
        raise SystemExit(f"FAIL {name} has no MG_FLOORS")
    got = {}
    for key, num in re.findall(r"(passPrecipIn|passSnow6In)\s*:\s*(\d+)", m.group(1)):
        got[key] = int(num)
    return got


def main():
    v = floors(VIEWER.read_text(encoding="utf-8"), "viewer.js")
    m = floors(METEO.read_text(encoding="utf-8"), "meteograms.js")
    bad = []
    if v != WANT:
        bad.append(f"viewer.js floors {v}")
    if m != WANT:
        bad.append(f"meteograms.js floors {m}")
    if v != m:
        bad.append("viewer.js and meteograms.js floors differ")
    src = VIEWER.read_text(encoding="utf-8")
    if "MG_FLOORS.passPrecipIn" not in src or "MG_FLOORS.passSnow6In" not in src:
        bad.append("viewer pass chart does not read MG_FLOORS")
    met = METEO.read_text(encoding="utf-8")
    if "MG_FLOORS.passPrecipIn" not in met or "SCALE_FLOOR_SNOW6 = MG_FLOORS.passSnow6In" not in met:
        bad.append("meteograms.js does not use MG_FLOORS")
    if bad:
        print("FAIL")
        print("\n".join(bad))
        return 1
    print("OK  pass floors", WANT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
