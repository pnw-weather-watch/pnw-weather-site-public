# California pass view: how it would work on the site

Draft for Benjamin, Tue Nov 3, 2026 (PST). Style: Deep Ocean Night.
- **Current mock (v2):** `mocks/ca_passes_deep_ocean_v2.png` (2000 × 1562 px), made by `render_ca_passes_v2.py` from `ca_passes.csv` (rows with `status=included`).
- Earlier mock (v1, 22 passes, no roads): `mocks/ca_passes_deep_ocean.png` from `render_ca_passes.py`, kept unchanged for comparison.

## v2 changes (Benjamin: "Only include major pass names on major routes", "Add roads")
- **Pass list trimmed to 15 major named passes on major routes**, numbered north to south:
  1 Yuba Pass (SR-49) · 2 Donner Pass (I-80) · 3 Mount Rose Summit (NV-431) · 4 Spooner Summit (US-50, Nevada) · 5 Kingsbury Grade / Daggett Pass (NV-207) · 6 Echo Summit (US-50) · 7 Luther Pass (SR-89) · 8 Carson Pass (SR-88) · 9 Monitor Pass (SR-89) · 10 Ebbetts Pass (SR-4) · 11 Sonora Pass (SR-108) · 12 Tioga Pass (SR-120) · 13 Walker Pass (SR-178) · 14 Tehachapi Pass (SR-58) · 15 Tejon Pass (I-5).
- **Dropped** (kept in `ca_passes.csv` as `status=excluded` with an `exclude_reason`): Fredonyer (SR-36), Beckwourth (SR-70), Brockway Summit (SR-267), the old US-40 Donner Pass Rd duplicate, Conway Summit and Deadman Summit (US-395 summits), Sherman Pass (Forest Service road).
- **One Donner marker:** the I-80 summit point, labeled "Donner Pass" (GNIS calls that crest Euer Saddle; see CSV notes).
- **Roads:** I-80, I-5, US-50, US-395, SR-49 (Yuba Pass leg only, north of 39.25°N), SR-89, SR-88, SR-4, SR-108, SR-120, SR-178, SR-58, NV-431 and NV-207. Source: US Census TIGER/Line 2024 primary and secondary roads for CA and NV (public domain, `data/tiger/`). Short gaps where TIGER names an edge by its local street name are bridged with straight connectors under about 8 km. Drawn as a pale line with a dark casing, under the pass labels; leader lines are now amber so they don't read as roads.
- **Route shields:** Interstate = blue, US route = white, California route = green, Nevada route = gray, with a legend at the bottom of the panel. Shields are placed automatically on the road, clear of pass badges, labels, leader lines, cities and other shields. NV-207 has no shield (its whole length sits under the Tahoe label column), and US-50 is shielded once, in Nevada; both routes are named in the panel.
- **Frame** tightened in the north to 40.15°N (nothing north of Yuba Pass now). Redding dropped as an orientation city (it sits north of the new frame).
- Footer credit added: "Roads: US Census TIGER/Line 2024 (public domain)".
- No `partial`-verified passes remain in the list, so the asterisk footnote is gone.

## What the mock shows (v1 description; v2 differences above)
- **Frame:** Sierra Nevada, 122.75°W–116.15°W, 34.45°N–40.75°N, in Mercator. It runs from Fredonyer Pass in the north to Tejon Pass in the south.
- **Fill:** GFS 0.25° 2 m temperature. The run is 12Z (Tue Nov 3, 4:00 AM PST), F012, valid Tue Nov 3, 4:00 PM PST. It uses the shared t2m bins with the hard 32 °F break and a labeled 32 °F line.
- **Relief:** a hillshade computed from USGS 3DEP elevation (public domain), shown on land only. Credit: "Relief: USGS 3DEP (public domain)".
- **Pass markers:** 22 numbered amber badges, each labeled "Name elevation′ temp°". Around Tahoe the passes sit close together, so their labels stack in two columns with leader lines back to a dot at the true pass point.
- **Side panel:** lists the passes north to south: number, name, highway, pass elevation, GFS terrain elevation, temperature chip (colored from the same scale) and surface gust in mph.
- **Model value:** GFS 2 m temperature and surface gust at the **nearest 0.25° grid point**. The 2 m temperature sits on GFS model terrain, which is smoothed. In this run that terrain is anywhere from 2,135 ft below to 1,145 ft above the real pass. No lapse-rate adjustment is applied. Passes close together can share a grid point (for example Donner Summit and Donner Pass, or Echo, Luther and Carson). The panel note on the image says this.

## On the site
1. **Pass picker.** A "Passes" tab under California, with an A–Z list and a north-to-south list grouped as: Northern Sierra and Tahoe (Yuba, Donner, Mount Rose, Spooner, Kingsbury/Daggett, Echo, Luther, Carson), Central Sierra (Monitor, Ebbetts, Sonora, Tioga), and Southern Sierra and Grapevine (Walker, Tehachapi, Tejon). Clicking a badge on the map or a row in the panel opens that pass's card. On a phone the panel becomes a list under the map, and the map shows badges only, without text labels.
2. **Pass card (meteogram).** One card per pass, using the same layout as the town meteograms:
   - 2 m temperature with a 32 °F line, wind and gust, precipitation and snowfall, snow level or freezing level against the pass elevation, and cloud.
   - **Ensemble plume:** GEFS (31 members) and ECMWF ENS (51 members) as thin member lines, with a bold mean and median and a 10–90% band. A second tab shows the chance of at least 1, 3 or 6 inches of snow per 6 h.
   - Deterministic models drawn over the plume: GFS, ECMWF IFS, AIFS, NBM (CONUS 2.5 km), HRRR (out to 48 h) and RRFS once it's stable.
   - Header: name, highway, pass elevation, and each model's terrain height at the chosen point, so the elevation gap is always visible.
3. **Point choice per model.** The default is the nearest grid point. Before launch, test two other options: bilinear interpolation, and the nearest land point with the smallest elevation difference within one grid cell. Then pick one for each model and state it on the card. A lapse-rate correction (for example, the model's own 2 m–850 mb lapse rate) could be an optional toggle, labeled "adjusted". It would never replace the raw model value.
4. **Map products for the pass frame:** 2 m temperature (this mock), snowfall (6 h, 24 h and total), QPF, wind gust, snow level and freezing level, all on the same frame. The pass badges stay on every product, and the value in each label switches to the product's field.

## Data sources (all public, no sign-in)
- NOAA GFS / GEFS (AWS `noaa-gfs-bdp-pds`, `noaa-gefs-pds`), NBM (`noaa-nbm-grib2-pds`), HRRR (`noaa-hrrr-bdp-pds`), RRFS (`noaa-rrfs-pds`). Credit: "Data: NOAA (public domain)".
- ECMWF IFS, ENS and AIFS open data. Credit: "Data: ECMWF, CC BY 4.0 (modified)", plus ECMWF's required wording.
- Pass points: USGS GNIS (public domain), checked against USGS 3DEP point elevations (EPQS) and Wikipedia's published elevations. See `ca_passes.csv`, columns `verified`, `dem_check_ft` and `notes`.
- Basemap: Natural Earth. Relief: USGS 3DEP. Roads: US Census TIGER/Line 2024 (public domain).

## Out of scope
- **No road conditions, chain controls, closures or cameras.** Caltrans QuickMap/CWWP2 and NDOT data aren't added, and WSDOT is out of scope for California. They can be revisited only if their terms are confirmed as public domain or Benjamin approves the terms. Seasonal closures (Tioga, Sonora, Ebbetts, Monitor) appear as a static note in the CSV only, not as live status.

## Open items
- Resolved in v2: Fredonyer, the US-395 summits and the three `partial` passes (Brockway, Deadman, Sherman) are excluded. Tejon is kept as the I-5 crossing.
- Benjamin to confirm the 15-pass list. Possible adds on major routes: Emigrant Gap (I-80) or Carson Spur (SR-88); both are points on routes already shown.
- Road gaps are bridged geometrically for the mock; for the site, consider Caltrans/NDOT state highway centerlines only if their terms are confirmed public domain, otherwise keep TIGER.

## v3 (Tue Nov 3, 2026, 12:40 PM PST)
- Script `render_ca_passes_v3.py` (+ `shields_v3.py`, `data/fetch_ecmwf_snow_v3.py`), image `mocks/ca_passes_snow360_ecmwf_v3.png` (2100 x 1620).
- One main pass per route: ca_passes.csv columns v3_status / v3_num / v3_exclude_reason (v2 columns unchanged). SR-89 = Luther Pass (open year-round; Monitor closes in winter). Dropped Spooner (US-50 shown at Echo) and Kingsbury/NV-207 (minor connector).
- Data: ECMWF IFS 0.25 open data, 12Z Nov 3 2026 run (4:00 AM PST), F000 and F360 (valid Wed Nov 18, 4:00 AM PST). sd (m water equiv., paramId 141) and rsn (kg/m3, paramId 33); depth = sd*1000/rsn; change = F360 - F000, m to in. Nearest 0.25° grid point, no elevation correction.
- Caveat: open-data sd is 9-bit packed in 1/32 m SWE steps (1.23 in SWE), so depth changes jump in about 5-7 in steps; small snow (<1.2 in SWE) reads as 0. Snowfall (sf) is packed much finer (11 bits) if a smoother product is wanted.

## v5 (Tue Nov 3, 2026, 12:45 PM PST): monetization-safe credits and decluttered image
`mocks/ca_passes_snow360_ecmwf_v5.png` from `render_ca_passes_v5.py`. It keeps the v4 scale and has no terrain. Credits follow `LEGAL_RULES.md` / `CREDITS_LEGAL.md`.
Caveats moved off the image (the image keeps one short line, "Nearest 0.25° grid point, no elevation correction; values move in steps of about 5-7 in."):
- Snow depth = ECMWF sd (snow water equivalent, m) ÷ rsn (snow density) × 1000, F360 minus F000, in inches; the model's own depth, not a 10:1 ratio.
- ECMWF open data packs sd in 1/32 m (1.23 in) SWE steps, so depth changes jump in about 5-7 in steps.
- Values are at the nearest 0.25° grid point. Model terrain sits 1,626 ft below to 1,698 ft above the real passes, with no elevation correction. Echo, Luther and Carson share one grid point.
- Per-pass SWE change and model terrain (removed from the panel): Yuba +6.2 in / 7,062 ft · Donner +4.9 / 6,774 · Mount Rose +3.7 / 7,285 · Echo, Luther, Carson +4.9 / 8,131 · Ebbetts +4.9 / 8,453 · Sonora +4.9 / 8,751 · Tioga +4.9 / 9,506 · Walker 0 / 4,930 · Tehachapi 0 / 3,221 · Tejon 0 / 5,742.

## v6 (Tue Nov 3, 2026, 12:52 PM PST): site-wide snow scale
`mocks/ca_passes_snow360_ecmwf_v6.png` from `render_ca_passes_v6.py`. The layout, legal credits (two ECMWF lines), lack of terrain and one-line caveat are the same as v5. The fill, chips and key now use THE site snow scale in `snow_scale.py` / `snow_scale.json`: 18 gain bins up to 60 in, white for 60+, and 8 melt bins. The key is full width with every edge labeled. The white bin is outlined, with a thin dark contour at 60 in. See STYLE_RULES_DRAFT.md "v6". This run peaks around +31 in, so the 36 in and up pinks and the 60+ white do not appear on the map.

## v7 (Tue Nov 3, 2026, 12:58 PM PST): 56-color site snow scale
`mocks/ca_passes_snow360_ecmwf_v7.png` from `render_ca_passes_v7.py`. The layout, credits, lack of terrain and caveat line are the same as v6. Fill, chips and key use the v7 `snow_scale.py`: 56 colors with labels at KEY_TICKS only. The fill now reads as a smooth ramp. The 12-16.5 in indigo still forms a darker ring (see STYLE_RULES_DRAFT.md v7). Note: `render_ca_passes_v6.py` imports `snow_scale`, which is now v7. To re-render v6 exactly, change that import to `snow_scale_v6 as SS`.

## NBM Northern California pass view v1 (Tue Nov 3, 2026, 1:12 PM PST)
- **Image:** `mocks/nbm_norcal_passes_temp_deep_ocean_v1.png` (2100 × 1479 px), made by `render_nbm_norcal_passes_temp_v1.py` (default `tmax`).
- **Variant:** `mocks/nbm_norcal_passes_tmin_deep_ocean_v1.png` (`... tmin`; data fetched by `data/fetch_nbm_tmin_v1.py`).
- **Data:** NOAA NBM CONUS 2.5 km core, 12Z Tue Nov 3 run, on its native Lambert grid (no downsampling).
  - TMAX: 12-hr max F024–F036 = Wed Nov 4, 4 AM–4 PM PST.
  - TMIN: 12-hr min F036–F048 = Wed Nov 4, 4 PM to Thu Nov 5, 4 AM PST.
  - Same t2m scale as the NBM PNW view, with the 32 °F line.
- **Frame:** 124.45–118.05°W, 37.55–42.30°N, Mercator. Same Deep Ocean Night look, no terrain shading, shields from shields_v3, and TIGER 2024 roads for CA, NV and OR (`tl_2024_41_prisecroads` added to `data/tiger/` for I-5 into Oregon).
- **Passes (one per major route, north to south):** Siskiyou Summit I-5 (Oregon, about 4 mi north of the CA line; Wikipedia infobox and GNIS 1127005: 42.06056 N, 122.60583 W, 4,310 ft). Then the v3 set north of 37.8 N: Yuba SR-49, Donner I-80, Mount Rose NV-431, Echo US-50, Luther SR-89, Carson SR-88, Ebbetts SR-4, Sonora SR-108, Tioga SR-120.
- **Pass values:** NBM value at the **nearest native 2.5 km grid point. No elevation correction.** The NBM grid terrain is smoother than the real pass, so a grid point can sit lower or higher than the summit.
  - Echo Summit reads warm (high 56 °F vs 46 °F at Luther) because its nearest grid point is about 1 km east, toward Lake Valley.
  - Echo, Luther and Carson are now separate grid points (not shared, as they were on the 0.25° ECMWF grid).
- **Not added:** a US-97 pass (Grass Lake / Mount Hebron Summit), because no verified coordinates or elevation were found this session. SR-36, SR-70 and SR-299 passes stay out as minor routes, per earlier ca_passes.csv decisions.
- **Credits:** none on the image. NOAA NBM, US Census TIGER, USGS GNIS and Natural Earth are public domain, and the fonts are OFL (LEGAL_RULES rule 5). CREDITS_LEGAL.md already lists NBM and TIGER, so it is unchanged.

## NBM Northern California snow pass view v1 + temp/tmin v2 (Tue Nov 3, 2026, PST)
- **Images (all 2100 × 1479 px), one script `render_nbm_norcal_passes_v2.py [snow|tmax|tmin]`:**
  - `mocks/nbm_norcal_passes_snow_deep_ocean_v1.png` (snow)
  - `mocks/nbm_norcal_passes_temp_deep_ocean_v2.png` (tmax), `mocks/nbm_norcal_passes_tmin_deep_ocean_v2.png` (tmin). v1 files untouched.
- **Snow field:** NBM 12Z Tue Nov 3 run, ASNOW (total snowfall) 6-h accumulations F000-F006 ... F258-F264, 44 messages summed
  (`data/fetch_nbm_asnow_v1.py`), m -> in. F264 is the last NBM step with snowfall, so this is the longest window:
  Tue Nov 3, 4 AM PST to Sat Nov 14, 4 AM PST. Native 2.5 km grid, no smoothing. Fill = `snow_scale.build("amount")` (v7, < 0.1 in no fill,
  white 60+ with a thin dark 60 in edge; this run peaks ~40 in so no white shows). Contoured with `transform_first=True` and < 0.1 in masked:
  projecting the hole-filled 0.1-0.25 in polygon from lat/lon made cartopy flood the whole map with one band.
- **No low-snow variant:** passes get 9-24 in (Siskiyou 0.7 in) and the snowiest 24/48/72 h windows all end at F264
  (Sierra max 12.7 / 22.1 / 30.0 in), so the full F000-F264 total already is the most-snow view.
- **Pass values, method (same for all passes and all three variables), `pass_sampling_v1.py`:** among NBM grid points within 3 km of the summit
  (4-5 points), use the one whose terrain best matches the signed summit elevation. NBM core files have no terrain field, so a cell's terrain = mean
  USGS 3DEP elevation over the 2.5 km cell (`data/3dep_norcal.tif`, ~300 m, public domain, `data/fetch_3dep_norcal_v1.py`; sampling only, not drawn).
  Image caveat line: "NBM 2.5 km point within 3 km whose terrain best matches the summit elevation."
- **Per-pass (summit ft | chosen cell ft, distance | snow in | v1-style nearest cell ft, snow | 3 km max snow | tmax / tmin F):**
  Siskiyou 4310 | 4372, 1.2 km | 0.7 | same | 2.6 | 48 / 41 · Yuba 6710 | 6588, 2.0 | 8.7 | 6860, 9.4 | 9.9 | 51 / 32 ·
  Donner 7239 | 7344, 0.8 | 13.1 | same | 15.6 | 50 / 31 · Mount Rose 8911 | 8871, 2.2 | 14.7 | 8814, 14.9 | 15.4 | 42 / 27 ·
  **Echo 7382 | 7573, 1.5 | 17.2 | 6899, 8.1 | 17.2 | 47 / 33** (v1 read 56 / 29 from the Lake Valley cell) · Luther 7740 | 8055, 0.6 | 18.8 | same | 21.5 | 46 / 29 ·
  Carson 8574 | 8582, 0.7 | 23.3 | same | 24.7 | 43 / 28 · Ebbetts 8736 | 8642, 1.3 | 21.9 | 8591, 19.6 | 23.0 | 41 / 26 ·
  Sonora 9624 | 9658, 2.1 | 24.4 | 9717, 27.0 | 27.9 | 42 / 26 · Tioga 9945 | 9970, 2.4 | 20.7 | 10180, 22.4 | 23.4 | 45 / 27.
- **Road gaps (Benjamin: "gaps in some roads ... such as I-5"), causes:**
  1. TIGER puts one FULLNAME per edge. I-5 from Redding to Lakehead is "I- 5 Scn" (scenic designation), and v1 matched only "I- 5": a ~64 km hole. Other edges carry local
     names or variants ("Hwy 89", "E Hwy 4", "Hwy 395", "Highway 120 Rd"; SR-120 east of Tioga Pass is only "Tioga Pass Rd").
  2. v1 `_merge` only drew straight bridges under 0.08° (~5 mi), so longer renamed stretches stayed open.
  3. v1 matched state routes in every state file, which pulled in unrelated NV 49 / NV 120 pieces.
  4. The road network's T-junctions sit mid-line in TIGER, and v1 joined pieces only at shared end nodes.
  (State-file boundaries were not a cause here: CA/NV/OR edges meet at shared points.)
- **Fix, shared module `roads_v2.py` (use it for every new view):** route-number name regex with direction prefixes and suffixes plus "Scn",
  per-route aliases for verified local names, mainline only (Bus/Alt/Old/Byp/Hov/Spur/Loop/Trk excluded), state routes from their own state file only.
  The whole TIGER network is noded (split at every crossing), and each leftover gap is filled along the shortest real road path (≤ 1.35 × straight + 3 km,
  gaps up to 120 km). Only gaps under 2 km (~6 px) get a straight join. Zero-length / < 300 m isolated slivers are dropped.
  The TIGER primary-roads file was not needed: primary roads are a subset of prisecroads.
- **Audit:** `audit_roads_v2.py` writes `audit_roads/<route>.png` (route in red over all TIGER roads, loose ends circled) plus zoom crops
  (`audit_roads/zoom_*.png`). I-80, I-5, US-50, US-395, US-97, SR-49 (clipped ≥ 39.25), SR-89 (38.5-39.35), SR-88, SR-4 (now unclipped; the v1 37.9 N clip
  cut it into pieces across the Delta), SR-108, SR-120 and NV-431 each make one connected line. Remaining loose ends are real termini, clip edges or ramp stubs.
  US-97 is checked but not drawn on this view.
- **Not changed:** the older CA pass scripts (`render_ca_passes_v2-v7.py`) and `render_nbm_norcal_passes_temp_v1.py` keep their v1 `_merge` so their images reproduce.
  Switch them to `roads_v2.route_geoms` on their next version.
- **Credits:** none on the image (NBM, TIGER, GNIS, Natural Earth and 3DEP are public domain; OFL fonts). CREDITS_LEGAL.md has a new 3DEP row for sampling use.
