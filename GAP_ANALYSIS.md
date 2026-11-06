# Gap analysis: this site vs wx-forecast-maps

Compared `pnw-weather-site` (this repo, including the Hawaii registration camera) with Weather Bot's methods note and the reference copies of `fast_encode.py`, `fast_cycle.py`, `viewer.js`, and `GUARDS.md`. Nothing in the methods note is tagged `[unverified]` in the body. Where the note and the reference code disagree, the code wins. That happened once: the note describes `findStepWithProduct` during playback, and the reference `go()` does not. We did not add it.

Benjamin's choices for this site stay as they are. They are listed under each stage as "kept".

## 1. Ingest and frame readiness

**What we do.** `fast_cycle.avail` reads the first 11 bytes of the idx or index. `target_cycle` takes the newest cycle in the last 36 hours whose first step is available. `DUE_MIN` is hrrr 45, rrfs 60, nbm 55, gfs 200, ifs 330, ifs9 420, aifs 320, eps 380, aens 350, gfsw 215. Watch starts 60 minutes early and runs 6 hours. HTTP retries live in `temp_maps.get`.

**What they do.** The same functions and the same minute table. Confirmed in the reference `fast_cycle.py`.

**Change.** None. The GitHub schedule in `.github/workflows/fast-models.yml` is still commented out here. Their workflow fires at :07, :22, :37, and :52. Uncommenting that cron is the frame-watcher branch (`cursor/frame-watcher-82e3`). This change does not touch that file.

## 2. Processing and derived fields

**What we do.** Lat/lon grids use cell centers: `(90 - lat) / res` and `(lon mod 360) / res`. Lambert grids use projected meters. The published crop only grows. Snow, Kuchera, freezing rain, precip type, lightning proxy, IVT, waves (land sentinel −0.5), snow-depth change, and the ensemble means are the same field helpers.

**What they do.** The same formulas. The methods note's unit examples (K to F, m/s to mph, wave meters to feet, IFS snow water × 10) match `FIELDS` in both encoders.

**Change.** None in the field math. Wave products now set `min_show` to 0 so the −0.5 land sentinel is not painted. That is the registration work, and it matches their rule that land is a sentinel and the basemap shows through.

## 3. Encoding

**What we do.** `q8` is the 0–255 linear quantize. Precip totals in `SQRT_FIELDS` store a square-root code and the viewer undoes it. Up to three fields share one RGB PNG (`PACKS`). `run.json` lists only the unbroken prefix of steps.

**What they do.** The same quantize, the same sqrt set, the same pack names, the same unbroken prefix.

**Change.** None.

## 4. Rendering and registration

**What we do.** One camera per view (`tools/forecast/camera.py`). The LUT, the land PNG, the coast PNG, and the town and buoy pixels come from that figure. Land is a white GSHHG full-resolution polygon on every product. The map is 1920×1080, full bleed, color bar on top, valid time under the map in Pacific time. Static layers are also saved at 2× from the same figure. The browser stacks the layers and does not reproject.

**What they do.** One `TM.frame` per view, LUT every 8 pixels, 1× and 2× from the same figure, Natural Earth coast (10 m on the Washington-like views, 50 m elsewhere). Their basemap credit says Natural Earth.

**Change.** Kept. White GSHHG land, the 1920×1080 full-bleed frame, the locked temperature scale, and the views in `regions/regions.json` are this site's choices. We do not switch the shore back to Natural Earth.

## 5. Publishing, R2, manifests

**What we do.** R2 keys are `manifest.json`, `static/base_`, `static/land_`, `static/towns_`, `static/x2/`, `static/lut_`, `static/key_`, `static/wave_views.json`, and `runs/{model}/{cycle}/`. `publish_static.py` merges with an ETag and does not replace the run list. `fast_cycle` keeps 2–4 runs, slims older ones, and writes `progress`. `/d/` cache is 30 seconds for manifest and run.json, immutable for `runs/`, one day for static.

**What they do.** The same layout, minus our `static/land_` layer, plus a Studio view file we do not publish. Same cache header values. Confirmed in our `functions/d/[[path]].js` against the methods note.

**Change.** None. `static/land_` is the white GSHHG fill and stays.

## 6. Viewer

**What we do.** Boot loads the manifest with `cache: "no-cache"`. Every 2 minutes the manifest is read again. Every 60 seconds an incomplete run's `run.json` is read and new hours are appended. Play steps every 250 ms. Missing 2× art falls back to 1×. Compare stays as two synced maps.

**What they do.** The same timers and the same 2× fallback. Their `go()` is the same one-line step change. The note's "jump to the next hour that has the product" is not in that function, so we left `go()` alone.

**Change.** Pass charts. Their viewer keeps the axis floors in one object, `MG_FLOORS` (`passPrecipIn: 3`, `passSnow6In: 12`), and the pass precip axis is at least 3 inches. Ours had the 12 inch snow floor written as a bare number, and the pass precip axis had no 3 inch floor. Both pages now share `MG_FLOORS`, and a pass precip axis starts at 3 inches.

Not copied: Studio, social loops, TV mode, and the Washington forecast-map product (`wafc` / `wamaps`).

## 7. QA guards

**What we do.** `qa/guard.py` reloads the map and checks that the view, product, and run survive, that the map fits the viewport, and that the color keys stay separable. It did not know the pass-chart floors, and its default desktop size was 1440×900.

**What they do.** Three browser guards (refresh, layout, pass chart), a scoped file map, a known-versus-new baseline, a deploy lock, and `ship.sh`. Most of that drives Studio and their Pages deploy. We do not have Studio, and we do not run their ship script.

**Change.** Ported the part that applies here. `qa/pass_floors_test.py` fails if `viewer.js` and `meteograms.js` disagree on `MG_FLOORS` or stop using it. `qa/guard.py` now opens at 1920×1080 and checks `window.MG_FLOORS` on the page. The Studio refresh groups, the WA-maps groups, the deploy lock, and `ship.sh` are not copied. `qa/GUARDS.md` says which checks those were compared with.
