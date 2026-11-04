# Theme proposal: "Coastal Daylight" (v1, Tue Nov 3, 2026 ~8:20 PM PST)

This is the one unified theme for every map on the new PNW / California / Hawaii site.
- **What it's built on:** the look Benjamin has already approved: white base, bright colors, knots aloft, the canonical `anom_scale.json` v6 and `temp850_scale`.
- **What it borrows from INDEX.md:** the airy "Island Light" direction and the vertical right-hand key.
- **What it avoids:** "Pacific Coastal" and "Night Chart" both need a dark base, which conflicts with the approved white-base decision. Snow, mountain passes and radar keep their dark base, recolored to these tokens.
- **Original work:** none of Benjamin's ramps, breakpoints, header and corner-tag layout, key position, fonts or H/L style is used. The handoff examples were looked at for reference only, and nothing was copied.

## Ranked product list (from `/workspace/handoff_examples/INDEX.md`; the ranking is an estimate)
| Rank | Product | Our status | Free data to build it |
|---|---|---|---|
| 01 | 2 m temperature | **Sample in this theme** (`theme_cd_t2m_pnw_v1.png`) | GFS TMP 2 m (also HRRR / NBM, NOAA, public domain) |
| 02 | MSLP + precip | **Sample in this theme** (`theme_cd_mslp_precip_pnw_v1.png`) | GFS PRMSL + APCP 6 h |
| 03 | Total precip (QPF) | Not yet; uses the same 6 h precip ramp, extended | GFS APCP totals |
| 04 | 500 mb heights anomaly | Mocks done (ref_style v5, canonical anom_scale) | GFS + PSL R1 climatology |
| 05 | Snow | Mock done (NBM passes snow, dark base) | NBM / GFS (NOAA) |
| 06 | Wind gusts | Partial (MSLP + 10 m wind mocks) | GFS GUST surface |
| 07 | 850 mb temps | Mocks done (anomaly v6, temperature v1) | GFS |
| 08 | Sea-level pressure | Partial (MSLP + wind mocks); the anomaly needs the free PSL slp LTM | GFS + PSL |
| 09 | Precip type | Not yet | GFS CRAIN / CSNOW / CICEP / CFRZR |
| 10 | Ensemble mean | Not yet | GEFS (NOAA). ECMWF open ENS is CC-BY 4.0 (needs a credit line; ask first) |
| 11 | Ensemble lows / members | Not yet | GEFS members |
| 12 | Member grids | Not yet | GEFS / NBM |
| 13 | Meteograms | Not yet | GEFS |
| 14 | Jet (300 / 250 mb) | Mocks done (jet300, knots) | GFS |
| 15 | Waves | Not yet | GFS-Wave (NOAA) |
| 16 | SST | Not yet | NOAA OISST (public domain) |
| 17 | Observations | Not yet | NOAA METAR / MADIS public feeds (a **new source**; report before use) |
| 18 | Radar / satellite | Not yet (dark base) | MRMS, GOES (NOAA); GIBS GeoColor with its credits |
| 19 | CAPE / severe | Not yet | GFS / GEFS CAPE |

## Theme tokens
- **Colors:**
  - Ink (titles, isobars, town labels): #0B2545.
  - Muted text: #5B6B7C.
  - Accent (header rule, region name, 32°F tick): teal #1F9E8F.
  - Land: #FFFFFF.
  - Ocean and lakes: sea-glass #EAF4F4.
  - Lines: coast #7D8B99, country #98A4AF, state #B5BEC7.
  - H: navy #0B2545. L: coral #E4572E.
- **Font:** Atkinson Hyperlegible (SIL Open Font License) for everything. It's a very legible humanist sans, unlike geometric bold caps.
  - Title: Bold 30, sentence case.
  - Subtitle and run line: Regular 14.5.
  - Town chips: Bold 14 on rounded white 82% chips.
  - Contour labels: Bold 12.5.
- **Header:**
  - Left: a navy rounded **time tile** showing "+24h" with the valid weekday and hour under it.
  - Next to it: the sentence-case title, with the model and run line below.
  - Right: the region name in teal, with the full valid time below.
  - A 2.5 px teal rule under the header.
  - No corner forecast-hour tag and no logo box.
- **Key:** a vertical **rounded capsule** on the right edge, with the unit on top and labels to its right.
  - The under/over ends are rounded caps.
  - The emphasized value (32°F) is bold teal.
  - It's never along the top or bottom-left.
- **H/L:** a filled disc with a white letter and white ring (H navy, L coral), with the pressure value in bold underneath in the same color.
  - Found from local extremes of smoothed pressure. Only placed where they aren't near the map edge.
- **Line weights:** coast 1.5, country 1.2, state 0.85, isobar 1.6 (white halo 3.6), 32°F line 2.6 (halo 4.6). Barbs as already set (knots).
- **Base map:** white land, sea-glass water, no terrain shading on white-base maps.
  - Dark-base products (snow, passes, radar) use ink #0B2545 as the base with the same fonts, header and key.
- **Fills:** light Gaussian smoothing plus 3× bicubic upsampling, so there's no speckle. Fills cover all terrain (high terrain is never blanked).
- **Footer:** data credits on the left ("Data: NOAA GFS 0.25° (public domain) · Basemap: Natural Earth", plus any credits a source legally requires). "Times in Pacific Time" on the right.

## How the color scales unify
All scales are our own, with these shared rules:
- **Cold to warm:** cold is always violet → indigo → azure → sky/ice, and warm is always lemon/apricot → orange → vermilion → wine.
- **Anomalies:** use `anom_scale.json` v6. White near normal, with the straight-grey and grey-purple extreme below.
- **Temperatures:** `temp850_scale` and the new 2 m scale use the same anchors, so 850 mb and 2 m maps read alike.
- **Precip:** sea-glass → lagoon → indigo → orchid → coral → gold. There's no green, which keeps it different from typical QPF ramps.
- **Color-blind QA:** each new scale is checked with `qa_cvd`, both neighbor to neighbor and every 3rd band.

| Scale | Bands | Smallest step, neighbors (normal / deutan / protan / tritan) | Smallest step, every 3rd band | Notes |
|---|---|---|---|---|
| 2 m temperature (−20…110°F, 2°F) | 65 + under/over | 2.9 / 2.0 / 1.7 / 2.3 (not a strict pass; fine gradient) | 9.7 / 6.2 / 5.6 / 6.7 (pass) | |
| 6 h precip (0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 3 in) | 13 + over | 15.3 / 7.0 / 6.3 / 10.8 (strict pass) | | First band vs white: 9.3 or more |

## Files
- `theme_coastal_daylight.py`: theme tokens, scales and the two sample renders.
- `theme_board_v1.py`: draws the theme board.
- `data/fetch_gfs_theme_v1.py`: the same NOAA AWS GFS source; adds TMP 2 m and APCP.
- `mocks/theme_cd_t2m_pnw_v1.png`, `mocks/theme_cd_mslp_precip_pnw_v1.png` and `mocks/theme_board_v1.png`.
