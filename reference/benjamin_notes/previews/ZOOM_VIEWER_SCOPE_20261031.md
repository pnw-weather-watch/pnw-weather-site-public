# Large zoomable model viewer, fast style, more towns as you zoom — scope (research only, 10-31-26 ~8:45 AM PT)
No build, nothing deployed for this part.

## What exists today
- viewer.js map zoom (since 10-29): wheel / pinch / double-tap 1-6x, drag pan, "Reset zoom". It is a CSS transform of the drawn canvas;
  the bitmap is re-rendered at RS = shown size x DPR x zoom (1..3x, <= 12 MP) ~200 ms after zooming stops; base/towns/keys have x2 PNGs.
- Town labels on maps: a STATIC towns_<view>.png per view (drawn by the encoder) + live numbers at a fixed list (manifest view.towns:
  WA view 43, Puget 41, Passes 29). Zooming only enlarges them; no new towns appear. Basemap is a raster PNG, so coasts/borders blur above ~3x.
- Already in the fast site: the Observations overlay (public/obs/obs.js, 62 KB, read-only copy of the old site's module) is a full vector
  zoomable map: own projection, basemap.json (1.35 MB: land/lakes/borders lo+hi detail, 699 Natural Earth places with rank, 6,448 GeoNames
  towns with population, 21 region names), wheel/drag/pinch, and a collision-box declutter where cities appear by rank tier and small towns
  "biggest first, smaller ones only as you zoom in". This is the engine Benjamin's idea needs; it just draws stations, not model fields.
- Place data on the box: /workspace/mapgen/data cities500 (GeoNames pop >= 500: WA 483, OR 262, ID 136, BC 552), Census 2023 Gazetteer
  (WA 639 places), census CDPs; wa_extras/town_pop.py tiers/pins/never-lists; basemap shapefiles (Census states/counties 500k,
  NE 10m borders/lakes, TIGER primary roads).

## Data resolution (cells across Washington, ~7.5 deg x 3.5 deg)
| model | grid in R2 (crop) | cells across WA | px per cell on 1600 px map at 1x / 4x |
|---|---|---|---|
| NBM 2.5 km | 805 x 666 | ~240 | ~6 / ~25 |
| HRRR / RRFS 3 km | 649 x 475 | ~200 | ~7 / ~30 |
| ECMWF 9 km (0.1 deg) | 391 x 231 | ~75 | ~20 / ~80 |
| ECMWF/GFS/AIFS/EPS 0.25 deg | 821 x 333 | ~30 | ~50 / ~200 |
- NBM/HRRR look good to ~6-8x with bilinear smoothing (town-scale detail is real). 9 km is fine to ~3-4x. 0.25 deg is smooth but adds
  no detail when zoomed: label it "coarse" or cap its zoom at ~3x. Data packs are 8-bit quantized per field (e.g. temp range 55 F -> ~0.2 F
  steps), fine for zoom. No new R2 data needed for zooming.

## Phone performance
- Field: recolor only the visible window at screen resolution (390x700 x DPR 3 ~ 2.5 MP) via the existing LUT + bilinear sample: ~10-20 ms.
- Vector basemap + ~150-300 labels per frame with a grid-bucket collision test: obs.js already does this smoothly on phones.
- Data per hour step is the same pack the viewer loads now (one PNG per field group), so scrubbing time stays fast. Keep canvas <= 12 MP.

## Recommended approach
Fork obs.js's map engine (projection, basemap, zoom/pan/pinch, declutter) into a new full-screen "Big map" page/mode of the fast site
(same dark fast style, same product/run/hour controls, values at towns). Draw the model field under the vector basemap by sampling the
R2 pack for the visible window (lon/lat -> grid i,j per model: ll grids direct, HRRR/RRFS/NBM via the existing LCC math in fast_encode).
Labels: town_pop pins/never lists first, then cities500 by population tiers per zoom (1x >= 50k, 2x >= 10k, 3x >= 2.5k, 5x+ all >= 500),
font size by tier and zoom, value at each label sampled at the town point (same rule as the posted maps). Passes always shown.

Phases (rough hours):
1. Prototype on the hidden preview (one model/variable: NBM or HRRR 2 m temp, one hour slider, WA): engine fork, field-under-basemap
   sampling for one grid type, population-tier labels with values, phone pinch: **4-6 h** (yes, "a few hours", because obs.js is reused).
2. All models/products: LCC + lat/lon sampling, products' palettes/keys from the manifest, wind barbs/contours (isobars from existing
   code paths), legend, URL state/share, Save image: 10-14 h.
3. Polish: town_pop tiers/pins/never-lists, pass summit correction toggle, label priority tuning, per-model max zoom, roads at high zoom,
   desktop full-screen layout, QA desktop/phone: 6-10 h.
Total ~20-30 h. Storage: + ~1-2 MB static (fork of basemap.json or reuse it), no per-run data, no CI change.

Risks: obs.js is a read-only copy of the old site's module (fork, don't edit it in place); contours/isobars need re-implementation in
the vector frame (current ones are baked per view); 0.25 deg models look blobby zoomed in; label clutter tuning near Seattle; iPhone
Safari still untested on a real device.

Recommendation: do the 4-6 h prototype first (NBM 2.5 km 2 m temp, best resolution, all data in R2), show Benjamin on the hidden preview,
then decide on phases 2-3.
