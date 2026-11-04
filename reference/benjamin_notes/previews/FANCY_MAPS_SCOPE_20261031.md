# Fancy WA maps on the fast site — scope (research only, 10-31-26 ~8:20 AM PT)
Nothing changed, pushed or deployed. Sources read: wa-forecast-map skill, /workspace/wa_extras/FORECAST_MAP_RULES.md (358 lines, locked style),
wa_extras/*.py, /workspace/alert_style.md, fast site (viewer.js 1289 lines, fast_encode.py, fast_cycle.py, R2 manifest/run.json via mirror 8772).

## How the two differ
- Fancy maps: server-side Python (wa_extras, ecmwf_venv), one JPG per request, 2400x1600 full state / 1600x2332 West / 1600x2400 East.
  Own downloads (NBM GRIB, ECMWF 0.1/0.25 open data, HRRR), label solver run per image, posted by hand (never auto-posted).
- Fast site: encoder draws STATIC layers once per view (base_<view>.png, towns_<view>.png, key_<model>_<prod>_<view>.png, 1x + x2, lut_<model>_<view>.bin);
  every run only uploads quantized field packs; viewer.js colors the field through the LUT and writes live town numbers on top.
  => A fancy map = new VIEWS + new PRODUCT presets. Mostly static assets plus viewer code; little or no new per-run data.

## 1. Fancy map types vs what the fast site has
| Fancy map | Data (fancy) | Fast site data already in R2 | Gap |
|---|---|---|---|
| NBM Predicted Low / High temps (full, west, east) | NBM 2.5 km hourly TMP; low = coldest 4-8 AM PT, high = daily max | nbm t2m hourly F1-36 then 3-hourly to F168; maxt, mint (NBM 12 h max/min) | low over 4-8 AM is exact only to F36; days 2-7 use 3-hourly t2m (5 AM PDT/4 AM PST step) or NBM mint (overnight min, slightly different definition) |
| Wind gusts HRRR / ECMWF / EPS (+ arrows, single hour or window max) | HRRR gust+u/v; ECMWF 0.25 10fg; EPS | hrrr/ifs/eps gust fields, gustmax/egust90, u10/v10 (hrrr, ifs, ifs9) | window max = client max over steps; arrows: fast draws barbs, fancy uses black translucent arrows |
| ECMWF 9 km rain totals, any window (also NBM/HRRR/GFS/ENS sources) | ifs 0p1 tp difference | ifs9 apcp (0-144 h, 3-hourly, newest run only); ifs/hrrr/nbm/gfs apcp | none for data; needs window picker + rain v3 palette (33 colors) |
| Kuchera snowfall | ECMWF sf x Kuchera ratio from Tmax over 2 m + 1000/925/850/700/600/500 hPa (above ground) | ifs9/ifs asnow (10:1), t2m, t925, t850, t700, t500 | no t1000/t600/surface-pressure mask -> client approx, or 1 new encoded field "ksnow" per step (exact) |
| Observed temps / lows so far this morning | IEM ASOS + HADS (+WSDOT), QC, NBM hourly fill corrected to stations | obs.js live station layer exists; nbm t2m F1 | NBM-corrected fill + station-to-town matching + QC would be new client code (no new R2 data) |
| Waves, BC Lower Mainland metric rain, Cascades/NE snow regions | separate renderers | ifs swh/wave dirs; bc views exist | lower priority |
| Weekend cards, alert maps (render_alert_map: aerial, NWS polygons, shields) | NWS point forecasts / alerts | — | not maps of model fields; keep server-side |

Styling elements the fast site lacks (all fancy types):
- Dark grey self-drawn base (forecast_base.py) with crisp WA/state borders; no dim of neighbors; neighbor fill on regional views.
- Dark top fade (~88% black, 22% height) behind title; portrait views: title + long horizontal top scale.
- Title Case templated titles ("Saturday Predicted Low Temps", "Estimated 72HR Kuchera Snowfall"), [MODEL] tag upper right, date/model lines bottom left.
- WAWX logo top-left at 40%; "Data: ECMWF (CC BY 4.0)" credit on ECMWF maps.
- Town labels: town_pop tiers (T1 38/39 px ... T4), no dots/leaders, centered + nudged, WA-only placement mask, official station pins (SEA, GEG, TIW, CLM ...),
  required/never lists, neighbor towns (OR/ID/BC) placed after WA, pass height correction (3.5 F/1000 ft) on temp maps.
- Value color rule (light blue <=32, red >85), fancy palettes (temps v8, rain v3, gust, Kuchera snow) and boxless legends.
- Summary lines bottom right ("Coldest town: X N", ties listed, "West side A to B in ...").

## 2. Client-side vs new data, and cost
- Static layers per new view: measured today 1 view across all 9 models = 9.1 MB (base 170 KB, towns 104 KB, LUT 175 KB, ~300 keys). Fancy views at 2400 px for
  ~4 models (nbm, hrrr, ifs9, eps) with ~6 products: est. 15-30 MB total for full/west/east. R2 now ~3.2 GB of 10 GB -> negligible.
- Per-run data: none for temps, gusts, rain, obs (reuse existing packs; LUT maps the new view onto the same grid).
  Exact Kuchera: +1 field per ifs9/ifs step ~ +1.4 MB per ifs9 run (keep=1), +1-2 min encode in the existing ifs job, no RAM change (ifs9 workers stay at 2 x ~3 GB).
- CI: static layers built once on the box (rebuild only when style changes; ~1-2 GB RAM, minutes); no extra workflow, fast-models keeps publishing as now.
- Client: 2400x1600 canvas = 3.8 MP; fine on desktop, phone needs the x1 layers and a scaled canvas (same trick as current x2 keys).

## 3. Proposed approach
"WA Maps" tab (or "Fancy" product group) in the fast viewer with presets: Lows, Highs, Gusts, Rain total, Snow (Kuchera), Observed.
Each preset = fixed view (full / West / East toggle) + model choice + day or window picker; viewer draws base -> field (fancy palette) -> top fade -> title/tag/logo/scale -> labels with live values -> summary lines.
Labels: run the wa_extras solver at encode time per view (positions sized for the widest value, e.g. "-10" / "12.34"), store towns_<view>.json; client fills in values; small risk of minor layout differences vs posted JPGs.
"Save image" already exists -> a fancy preset becomes a one-click postable JPG (posting still needs Benjamin's OK).
Auto-refresh: nothing new; presets always read the newest run from the manifest.

Phased plan (rough hours):
- P1 NBM Lows/Highs, full + West + East (static layer builder reusing forecast_base/region_maps/town_pop, label json, viewer preset mode, top fade/title/logo/scale/summary, pass correction, value colors, QA side by side with nbm_map.py final.jpg): 16-20 h.
- P2 Gusts (HRRR/ECMWF/EPS, hour or window max, arrows) + ECMWF 9 km rain windows (v3 palette, window picker, wettest/ties lines): 10-14 h.
- P3 Kuchera snow (client approx first; exact ksnow field if Benjamin wants parity): 6-10 h. Observed temps with NBM-corrected fill (port QC + matching to JS): 8-12 h.
- Leave server-side: alert maps, weekend cards, waves/BC metric/cascades special maps.
Total P1-P3 ~40-56 h.

Risks:
- Label parity: per-image solver vs precomputed slots -> some towns may differ from posted JPGs; mitigate with widest-value slots and side-by-side QA.
- NBM lows beyond F36 not hourly (definition drift); fast run only has newest ifs9 run (0-144 h) -> rain/snow windows limited to 144 h.
- Phone performance at 2400 px; Access-gated site (public posting still uses saved JPGs).
- Two style sources (Python rules + JS) can drift; keep FORECAST_MAP_RULES.md as the single source and share palettes via the encoder (keys/palettes exported to JSON).

Recommendation: build P1 first (NBM Lows/Highs full + West): most-posted map, all data already in R2, proves the static-label approach that every other preset reuses.
