# Studio zoom lock (Benjamin t2186u/t2187u), 11-03-26 — SHIPPED (t2188u) as production e63d04bd, commit 1aecf6f
Branch studio-zoom-lock off fd5108d (worktree /workspace/wx-models-site/zoomlock). Baseline preview of unchanged prod code: 3e5cf7ed. Fix preview: 5af1fbe3.
## Root cause
Studio's two-finger pinch (touch screens) read every finger on the screen (e.touches), not just the fingers on the frame. A finger on the
hour scrubber (or its < > buttons, the top hour slider, the other frame) plus a thumb/finger resting on a frame counted as a "pinch":
as the scrubber finger moved, the distance between the two fingers changed and the frame zoomed/re-centred (reproduced: 1.45x -> 1.0x, 1.0x -> 1.71x).
Also: Safari double-tap page zoom was possible on the scrubber buttons / frame headers (no touch-action), now off.
## Zoom paths in Studio (audit)
Intended: (1) the zoom slider over each frame (keyboard +/- 0 on a focused frame does the same, as in the hint), (2) two-finger pinch on a frame.
Not zooming: hour scrubber / slider / prev-next / arrow keys, product/model changes, drags (pan only, clamped), resize/fitFrames (CSS size only),
MP4 / camera preview (temporary camera override, never saved). Reset button = back to 1x (explicit).
## Tests (qa/zoomlock_20261103/)
- repro.py: Chromium, 12 model/product/view combos, clicks/double-clicks/drags at random scrubber positions + < > buttons + keys, view logged before/after.
  Baseline 252 checks: 0 changes (desktop mouse never zoomed); fix 1512x945@2x 252 checks 0 changes, phone 105 checks 0 changes, 0 console errors.
- touchreg.py (regression): iPhone 13 + iPad Pro 11, 4 models, both frames: finger on frame + finger on scrubber/buttons/slider/other frame must not
  change the view; a real pinch and the zoom slider must still zoom. Baseline FAIL (zoom jumps), fix PASS, 0 errors.
- Live QA on production (<PAGES_PROJECT>.pages.dev, e63d04bd, 9:39 AM PST): touchreg PASS (0 errors); click test 133 checks 0 changes 0 errors.
# Queued: snow cool scale (t2189u) — HIDDEN preview 6d3678df, branch snow-cool-scale (db4f0a8 on 1aecf6f), NOT pushed / deployed
- meteograms.js "Member View & Mean: Total Snow" (figSnowEns): SN_COLORS blues -> white (~10 in) -> purples; spread band ice blue #7fc4f2.
- Shots: qa/zoomlock_20261103/snow_shots/ (viewer 1512x945@2x, full chart, Studio meteogram 9:16 + 16:9). 0 console errors.
