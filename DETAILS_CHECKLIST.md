# Details checklist: every small detail of Benjamin's site and where it lives

Tick each line on the hidden preview. The paths are relative to the kit. The `viewer.js` line numbers are for the kit copy as built on 11-3-26, so search by the name if the lines have moved.
Column "Theme?" tells you whether the look comes from the theme layer (T) or is fixed logic you keep as is (L).

## All products (shared)
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Header: title, valid line (accent color), run line, badge "F+N" with the UTC hour | viewer.js `header()` ~1390; Python `house_style.header()` | T colors and font, L layout | [ ] |
| Color key along the top, under the header (key PNG per model/product/view; "@"-paths = site-shipped keys) | viewer.js `keyURL` ~477; fast_encode `static()` ~811 builds keys; `house_style.hbar/vbar` | T | [ ] |
| Credit line redrawn over the key's baked credit, current year, required credits per source | viewer.js `creditLines()` / `drawCredit()` ~879-905; footer `<details>` credits in index.html / compare.html | L (text from legal) | [ ] |
| Town names + numbers ("88" slots filled from the field), dot, side l/r | Python `temp_maps.towns()` ~403, `place_label()` ~385; fast_encode `town_call()` + slots; viewer number paint ~827 | T font | [ ] |
| Regional town tiers (population tiers, max labels) | `temp_maps.REGION_TOWNS` ← regions/regions.json `region_towns` | L via regions | [ ] |
| Label collision: names/numbers never overlap; dropped with a log line if no room | `temp_maps.place_label`, `_hits`; `house_style.clear_labels_near` | L | [ ] |
| Pacific NW tight town layer fix (towns_pnwt_v2.png + slots) | tools/fast/view_fixes.py (`pnwt_fix`), static/view_fixes.json, viewer `viewFixes()` ~176 | L | [ ] |
| Mountain passes: plum triangle + italic name + number, height-corrected values | `temp_maps.pass_labels()` ~516, `WA_PASSES` ~253; CA: regions.json `CA_PASSES` + fast_encode `town_call` "capasses" branch | L | [ ] |
| Pass Forecaster table + save | viewer.js `passCanvas()` ~1321, `mgSave()` | T colors | [ ] |
| Isobars every 2 mb, 0.75 pt, 1.6 pt halo, numbered along the line, label slide off H/L | viewer.js `ISO_MSLP` ~367, `drawIsobars/isoGeom/paintIsobars` ~1463-1528, `LAB_SLIDE` | T color, L rules | [ ] |
| H / L markers: letter + central pressure under it, declutter (stronger wins), edge pinning | viewer.js `HL_VIEW` ~1599, `hlGeom/hlDeclutter/paintHL` ~1602-1680; Python `find_centers` | T colors (`--map-hi/--map-lo`), L detection | [ ] |
| Wind barbs (5 kt rounding, flags 50, length 5.6 pt), density per view | viewer.js `drawBarbs/barb` ~1530-1574; `HS.BARBS_ACROSS` ← regions.json | L | [ ] |
| Flow arrows (waves direction, IVT) | viewer.js `arrow()` ~1546 | L | [ ] |
| Peak gust marker on gust products | viewer.js `drawPeak()` ~1370, `GUST_PIDS` | L | [ ] |
| Hover / tap readout with units | viewer.js `readout()` ~1134, `UNITS` | L | [ ] |
| Zoom / pan / pinch, sharp redraw (RS) after zoom, zoom lock | viewer.js `Z`, `applyZoom/zoomAt/setupPointer/setupTouchPinch` ~1151-1240, `wantRS` ~85 | L | [ ] |
| Save image (zoomed save at full sharpness), Share, phone save fallback | viewer.js `saveImage()` ~1254, `share()`, `showSaveView()` | L | [ ] |
| Missing hour jumps to the nearest hour, "not in this run" note + button to the nearest run | viewer.js `findHour()` ~724, `otherRunWith()`, `jumpNote()` | L | [ ] |
| Preload order (next 6 steps, then rest 3 at a time), load note | viewer.js `preload()` ~905, `loadNote()` | L | [ ] |
| View defaults: default view, fallback when a model lacks the view | viewer.js `S.view` ~39, `setLists()` ~404-436 (default from regions.json `default_view`) | L via regions | [ ] |
| Tabs order: Surface, Precip, Snow, Upper Air, Severe, Waves, Compare (no WA Maps, Studio, Social) | viewer.js `TABS` ~383, tab buttons ~410-425 | L | [ ] |
| Phone layout: menus, map sized between menus and slider (`fitPhone`) | viewer.js `fitPhone()` ~64; index.html CSS | T colors, L layout | [ ] |
| Credits/legal footer | index.html / compare.html footer; theme/michael_design/CREDITS_LEGAL.md, LEGAL_RULES.md | L | [ ] |

## Temperatures (2 m, highs/lows, feels-like, dewpoint, 850/925/700 mb, anomalies)
| Detail | Where | Theme? | OK |
|---|---|---|---|
| 2°F bands, 32°F line dashed (0°C on upper air), "lo to hi in view" in the run line | fast_encode product table ~1045-1245 (`freeze`, `extra`) | L | [ ] |
| Temperature palette | `theme.py` → `HS.TEMP_COLORS/T850_COLORS` (Michael temp850 v1; the 80-120°F extension is a kit addition) | T | [ ] |
| 850 mb below-ground grey | `temp_maps.BELOW_GROUND` | T (change in theme if wanted) | [ ] |
| Pass height correction 3.5°F/1000 ft (dewpoint 1°F) | temp_maps comment + `pass_labels(pass_corr)` | L | [ ] |
| 2 m / 850 anomaly reuse the anomaly family (t850a at 27x) | fast_encode ~955; `HS._anom_color` (theme) | T | [ ] |
| NBM temperature look (Michael) | theme/michael_design (render_nbm_* mocks in his folder); colors via temp scale | T | [ ] |

## Precip and QPF
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Rain totals bands (0.01, 0.1 steps to 4, 0.5 to 12), 18 in key ticks "4 6 8 10 12 15 18" | `HS.RAIN_LEVELS/RAIN_TICKS/QPF18_*` | T colors (Michael QPF + kit extension above 3 in) | [ ] |
| MSLP + precip: rain/snow/mix shares, rain key stops at 4 in | `HS.PTYPE_*`, `QPF_RAIN_MAX`, menu_maps | L | [ ] |
| Precip type nearest-neighbour sampling | viewer.js `sampleNN/sampleType` ~667-682 | L | [ ] |

## Snow
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Snow levels + colors | `menu_maps.SNOW_LEVELS/SNOW_ANCH` ← theme.py `apply_menu_maps` (Michael snow v6) | T | [ ] |
| Snow change map (loss/gain, -1..0.1 no fill, 60+ white with dark outline) | theme/michael_design/snow_scale_v6.json (wire into `dsnod` table, fast_encode ~1151: KNOWN GAP) | T | [ ] |
| Kuchera, 1 h / 6 h snow, snow level (freezing level - 1000 ft) | fast_encode ~980, ~1063-1180 | L | [ ] |

## Upper air and anomalies
| Detail | Where | Theme? | OK |
|---|---|---|---|
| 500 mb anomaly palette, under/over, ticks | `HS.ANOM_*` ← Michael anom_scale v6 (theme.py) | T | [ ] |
| MSLP anomaly key a80 (site-shipped "@mkeys") | viewer.js ~357-370; keys must be regenerated in your theme (KNOWN GAP) | T | [ ] |
| Climatology blend (months, t2m between hours) | viewer.js `climMonth/climAt` ~631-657; tools/forecast/make_clim*.py | L | [ ] |

## Waves (ECMWF, NOAA WW3, OISST)
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Buoys: NDBC list with names, placed after/before coast towns per view, CA + HI buoys included | viewer.js `BUOYS/WC_BUOYS` ~927-930, `drawBuoys()` ~931; `site/buoys_ndbc.json` (source: NDBC activestations.xml) | L | [ ] |
| Coast towns re-placed on wave maps, offshore value points 0.5 mi off, renames (Tatoosh Island etc.) | viewer.js `COAST_TOWNS/COAST_VIEWS/WAVE_KEEP/WAVE_RENAME/WAVE_DROP/OFFSHORE/OFF_BRG` ~979-1089 (WA-specific; add CA/HI entries: KNOWN GAP) | L | [ ] |
| "Max height: NN ft" line on wavemax products | viewer.js `MAXH_PIDS` ~1130 | L | [ ] |
| Swell period labels: white bold with dark core + drop shadow, hidden by rotated size near bar | viewer.js `paintIsobars` shadow_lab ~1522 | T | [ ] |
| Wave scales (height 0-50 ft, max 0-85 ft) | Michael theme_cd_waves_v4 → theme/qpf_wave_scales.json (`HS.WAVE_SCALES`; wire into fast_encode wave tables: KNOWN GAP) | T | [ ] |
| Wave views json | tools/fast/wave_views.py → static/wave_views.json; viewer `waveViews()` ~183 | L | [ ] |

## Ensembles and members
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Ensemble lows: member dots colored by pressure (DOT_BOUNDS/COLS/LABELS), mean L, low panel at the left edge | viewer.js `drawEns/lowGeom/paintLowPanel` ~1680-1838; ens_maps.py `low_panel` | T colors (DOT_COLS are Benjamin's; recolor), L rules | [ ] |
| Low detection per view (radius, prominence, smoothing) | viewer.js `LOWV` ~1715 (kit added pac/ca/hiw) | L | [ ] |
| Member lookup (type 1-50, arrows) | viewer.js `memUI()` ~518, `prepRun()` | L | [ ] |
| Member grids, ensemble chance maps | tools/forecast/member_grid.py, ens_maps.py; tools/fast/aens_members.py, eps_members.py | T | [ ] |

## Meteograms
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Page layout from the old Meteograms tab (old/base.css + forecast.css, now themed fonts) | site/meteograms.html, meteograms.js; web/forecast/*.css | T | [ ] |
| Town list (ICAO station points, passes at summit) | forecast/meteograms.py `TOWNS` ~30 and fast_encode town points (WA list: replace with PNW/CA/HI: KNOWN GAP) | L | [ ] |
| Member spaghetti, mean, snow hours | meteo_suite.py, meteograms.js `memTown/figPanels` | T colors | [ ] |

## Observations
| Detail | Where | Theme? | OK |
|---|---|---|---|
| Station plot, High, Low, Peak gust, Wind chill/heat index, MSLP toggles | web/forecast/obs/obs.js | L | [ ] |
| Radar (NOAA MRMS), Clean IR + GeoColor (NASA GIBS), water vapor (NOAA STAR), sharp-over-wide drawing, credits | web/forecast/obs/obsimg.js; reference/benjamin_notes/SATELLITE_TERMS_FINAL.md | L | [ ] |
| Region presets (Pacific NW, West + Western Canada, Vancouver Island + Puget Sound) | obs.js presets (add California + Hawaii: KNOWN GAP) | L | [ ] |
| Obs style rules | reference/benjamin_notes/OBS_STYLE.md | | [ ] |

## Standing style rules
- reference/benjamin_notes/STYLE_RULES.md (every product), OBS_STYLE.md, previews/ (decisions per feature: waves tab, WW3, member lookup, radar+GOES, save zoom, zoom lock, water vapor, small fixes).
- Michael's rules: theme/michael_design/STYLE_RULES_DRAFT.md, PRODUCT_LOOKS_PLAN.md, THEME_PROPOSAL.md, LEGAL_RULES.md.
- Benjamin's alert_style.md is about alerts and posting only, so it is not included (alerts are out of scope).
