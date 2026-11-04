# Product looks plan, v1 (Tue Nov 3, 2026, ~4:05 PM PST)

For Benjamin's new PNW / California / Hawaii model site (website only). This builds on the survey in `MODEL_SITE_SURVEY.md`. Deep Ocean Night base, new **Aurora Reef** vivid scales (`product_scales_v2.py`), and the v7 snow scale unchanged. These are design mocks only: nothing has been pushed or deployed.

## Summary

| # | Product | Tier | One-line reason | Model(s) | Required on-image credit |
|---|---|---|---|---|---|
| 1 | 300 mb wind (jet) + heights | **Core** | Benjamin asked for it; every site has it; it drives Pacific storms | GFS; ECMWF/AIFS open data | NOAA none; ECMWF CC BY text |
| 2 | 500 mb height anomaly + heights | **Core** | Benjamin asked; the standard pattern view for troughs and ridges | GFS, ECMWF, AIFS, GEFS mean | as above |
| 3 | 850 mb temperature anomaly + 32 °F line | **Core** | Benjamin asked; quick read of warm/cold air masses and snow-level setup | GFS, ECMWF, AIFS | as above |
| 4 | MSLP + 10 m wind | **Core** | Benjamin asked; the bread-and-butter storm map for the Pacific and coast | GFS, ECMWF, AIFS, RRFS (regional) | as above |
| 5 | 500 mb heights + absolute vorticity | **Core** | Standard everywhere; shows shortwaves that the anomaly view hides | GFS, ECMWF (vo) | as above |
| 6 | QPF (run total + 6/24 h) | **Core** | Most-viewed product for atmospheric rivers | GFS, ECMWF, NBM, RRFS | as above |
| 7 | Snowfall (v7 scale) | **Core** | Already approved scale; pass view + regions | NBM, ECMWF (sf), GFS | as above |
| 8 | 2 m temp (approved NBM look) + 2 m dewpoint | **Core** | Every site has them; temp look is already approved | NBM, GFS, ECMWF, RRFS | as above |
| 9 | Wind gusts | **Core** | Already mocked (NBM/RRFS); high-impact for the PNW | NBM, RRFS, ECMWF (10fg) | as above |
| 10 | IVT / PWAT (atmospheric river) | **Core** | West-coast signature product; Tropical Tidbits/Pivotal carry it | GFS (u, v, q levels or PWAT), ECMWF (q, u, v, tcwv) | as above |
| 11 | Snow level / freezing level | **Core** | Key for the Cascades/Sierra pass audience | NBM SNOWLVL; GFS HGT:0C isotherm | as above |
| 12 | 700 mb RH (+ omega optional) | Nice-to-have | Standard forecaster map; less needed by the general audience | GFS (RH, VVEL), ECMWF (r, w) | as above |
| 13 | 850 mb wind + temp | Nice-to-have | Useful for gap-wind and Santa Ana setups | GFS, ECMWF | as above |
| 14 | CAPE (surface / MU) | Nice-to-have | Thunderstorms are rarer here; still standard | GFS, RRFS, ECMWF (mucape) | as above |
| 15 | Simulated reflectivity | Nice-to-have | Popular, but only worthwhile from RRFS/HRRR at 3 km | RRFS | NOAA none |
| 16 | Total cloud cover | Nice-to-have | Cheap and popular for eclipse, astronomy and fog-burnoff questions | GFS, ECMWF (tcc) | as above |
| 17 | Waves: significant height + period (Pacific/Hawaii) | Nice-to-have | Hawaii and coast surf/marine audience | GFS-Wave; ECMWF wave stream | as above |
| 18 | SST + SST anomaly | Nice-to-have | Pacific/Hawaii context; slow-changing, so a daily map is enough | NOAA OISST v2.1 (NCEI) | NOAA none |
| 19 | MSLP + precip type | Nice-to-have | The usual US-site default; our MSLP + wind covers the core need | GFS (CRAIN/CSNOW…), ECMWF ptype | as above |
| 20 | 2 m temp anomaly | Nice-to-have | Engaging for posts; needs a 2 m climatology (R1 has one) | GFS, ECMWF | as above |
| 21 | 250 mb (separate from 300) | Skip | Duplicates 300 mb; 300 is closer to the PNW jet level in cold season | n/a | n/a |
| 22 | Soundings / cross sections | Skip (for now) | Large build (interactive); revisit after launch | n/a | n/a |
| 23 | Severe composites (STP, SRH) | Skip | Low value for PNW/CA/HI; adds clutter | n/a | n/a |
| 24 | ERA5-based anything | Skip | Needs a Copernicus sign-in (breaks rule 1) and adds a credit | n/a | n/a |

## Navigation (standard set from the survey)
Model → Region → Product menus; run selector (latest + 3 previous); forecast-hour slider with play/loop, ←/→ keys and preload; "previous run" and "model compare" side-by-side; PT times everywhere; all maps 2100 px wide (phone shows the same image scaled, with `ticks_375` keys). Click-for-sounding comes later.

## Regions
- **Whole Pacific** (Mercator centered on 180°, 120°E–100°W, 25°S–64°N): jet, 500 mb anomaly, MSLP + wind, IVT, waves, SST.
- **North America** (Lambert, ~160°W–62°W, 18–68°N, full rectangle): 850 mb anomaly, 500 mb views, 2 m anomaly.
- **Pacific NW, California, Hawaii, pass views** (existing frames): 2 m temp/dew, gusts, QPF, snow, snow level, reflectivity.
- Optional extra views (SoCal, Bay Area, Oregon coast, Big Island) are still pending Benjamin's earlier decision.

## Forecast-hour cadence
| Model | Cadence (what we'd render) | Source (free, no login) |
|---|---|---|
| GFS 0.25° | 3-hourly to F120, 6-hourly to F240 (F384 optional), 4 runs/day | AWS `noaa-gfs-bdp-pds` (NOAA NODD, CC0/public domain) |
| ECMWF IFS 0.25° open data | 3-hourly to F144, 6-hourly to F240 (00/12Z; F360 available), 06/18Z to F90 | data.ecmwf.int `ifs/0p25/oper` (CC BY 4.0) |
| ECMWF AIFS Single | 6-hourly to F360 (00/06/12/18Z) | data.ecmwf.int `aifs-single` (CC BY 4.0) |
| NBM CONUS 2.5 km | hourly to F36, 3-hourly to F192, 6-hourly to F264 | AWS `noaa-nbm-grib2-pds` (public domain) |
| RRFS 3 km CONUS | hourly to F60 (F84 at 00/06/12/18Z) | AWS `noaa-rrfs-ops-pds` (public domain) |
| GFS-Wave 0.25° global | 3-hourly to F120, 6-hourly to F240 (alongside GFS) | AWS `noaa-gfs-bdp-pds/…/wave/gridded/` (HTTP 200 checked today) |
| OISST v2.1 | daily | NOAA NCEI (public domain) |

## Anomaly climatology
- **Used in the mocks:** NCEP/NCAR Reanalysis 1 long-term means for 1991–2020 from NOAA PSL (`downloads.psl.noaa.gov`, no login, public domain), interpolated between mid-month means at 2.5°. Logged in `CREDITS_LEGAL.md` and **awaiting Benjamin's OK**.
- **Upgrade (recommended):** the same dataset's **daily** long-term means (`hgt.day.ltm.1991-2020.nc`, `air.day.ltm.1991-2020.nc`, `surface/slp.day.ltm.1991-2020.nc`; all HTTP 200 today). That removes the month-to-month smoothing.
- **SST anomaly:** OISST v2.1 with its own 1991–2020 daily climatology (NOAA, public domain). Terms to be verified before use.
- **Flagged and not used:** ERA5 / Copernicus CDS (needs an account, adds a credit); CFSR via NCAR RDA (needs a login). GEFS reforecast climatology is public domain but much larger to process, so it's an option later.
- A 2.5° baseline is coarse. It's fine for 500/850 mb on Pacific and North America frames, but not for 2 m anomalies on the regional frames.

## Palette family: "Aurora Reef" (Benjamin 11-03-26: brighter, vivid, original)
- **Wind family** (one 15-color ramp for every wind product; only the bins change): electric reef blue `#0B6FA8` → azure `#12ADEE` → glacier cyan `#3CCBFF`/`#7BE3FF` → periwinkle `#A08EFF` → ultraviolet `#9C55F7` → orchid `#C93CE6` → fuchsia `#EE34C6` → hot pink `#FF3F98` → coral `#FF5A6E` → tangerine `#FF7A3D`/`#FFA21F` → solar gold `#FFCC1A` → pale gold cap `#FFF27A`. The jet uses 60–220 mph and 10 m wind uses 10–120 mph. Below the first bin is transparent.
- **500 mb height anomaly:** glacier-cyan troughs (ice `#E6FFFF` → `#12C2E6` → deep teal) against fuchsia ridges (dusky plum `#3E2C48` → `#B92AAE` → `#FF70DC` → pink-white). The near-normal bins are dark ink (`#112530` / `#3E2C48`), so normal recedes and big anomalies glow.
- **850 mb temperature anomaly:** ultraviolet cold (lavender-white → `#8F72FF` → indigo) against ember warm (deep ember `#3A2618` → `#C64C08` → `#FF9A22` → solar gold → cream). Near-normal is again dark.
- **Snow:** the v7 scale stays exactly as it is.
- **Planned, not built yet:** QPF as a "lagoon" ramp (teal-ink → sapphire → ultraviolet → fuchsia → coral → gold, no green); IVT on the wind family ramp in kg m⁻¹ s⁻¹ starting at 250; CAPE as ember → magenta; dewpoint as ink → cyan → orchid; waves as reef blue → violet → coral; SST as ultraviolet → cyan → coral → gold.
- **How it differs from other sites:** there's no green or lime anywhere (Pivotal, Tropical Tidbits, Meteociel, weather.us and Benjamin's current site all run their ramps through green), no blue-white-red anomaly scheme, and no full-spectrum rainbow. Our signature is the cyan → ultraviolet → fuchsia → coral → gold run on a dark navy base.
- **Why it stays readable:** lightness climbs in steps within each hue segment, and every neighbor pair passes ΔE ≥ 5 in normal, deutan, protan and tritan vision (`qa_cvd_product_scales_v2.txt`: jet/wind10 min 6.4, h500 min 5.4, t850 min 6.6). The first wind bin stands off land and ocean by ΔE ≥ 35. The anomaly near-zero bins split by ΔE ≥ 9. Bright fills sit under dark contours with a pale halo (MSLP v2 rule), so lines stay readable on every color.

## Light vs dark base per product (Benjamin 11-03-26 ~4:07 PM PST: "white base maps for most products, except snow and others that you think would be better")
**Light base** (`Aurora Reef Light`, `product_scales_light_v1.py`, `render_gfs_products_light_v1.py`): white land `#FFFFFF`, near-white ocean `#F3F7FA`, thin gray coast/border/state lines `#8C98A3`, dark text `#0E1A26`, light header panel and colorbar.
**Dark base** (Deep Ocean Night): navy land/ocean, as in the earlier mocks.

| Product | Default | Why |
|---|---|---|
| 300 mb jet, 850 mb wind, 10 m wind, gusts | Light | Fill starts at a threshold, so most of the map is clean white; the wind ramp gets darker and more intense toward the top, which pops on white |
| 500 mb height anomaly, 850 mb temp anomaly, 2 m temp anomaly | Light | Near-normal fades to white, so only real anomalies get color; dark height lines read best on white |
| MSLP + 10 m wind, MSLP + precip type | Light | Black isobars and the H/L letters read best on white; barbs are clearer dark-on-light |
| 500 mb + vorticity, 700 mb RH, IVT/PWAT, QPF, dewpoint, CAPE, snow level/freezing level | Light | Threshold fills on white look clean and print-friendly; contours stay crisp |
| Waves, SST/SST anomaly | Light | Large ocean areas; white keeps the Pacific/Hawaii frames from feeling heavy |
| **Snowfall (all snow maps, v7 scale)** | **Dark** | The v7 top bin is white (60+ in) and the low end is pale pink/purple; both vanish on white |
| **Pass views (temp, lows, snow)** | **Dark** | Already approved dark; roads, shields and snow totals were tuned for it, and they share the snow look |
| **Simulated reflectivity** | **Dark** | The radar convention: bright echoes on a dark base read like a real radar screen |
| **Total cloud cover** | **Dark** | Clouds drawn as white/gray on dark read like a satellite image; white clouds on a white map would disappear |
| 2 m temperature (approved NBM look) | Dark for now | That scale was approved on the dark base. A light version needs a retune (its near-white bins would wash out), so it's a decision for Benjamin |

The site can still offer a light/dark toggle later (the earlier pending decision). This table sets the defaults.

### Aurora Reef Light palette changes (vs the dark Aurora Reef)
- **Wind family:** the low end is now a light but clearly tinted sky cyan `#BDE7FF` (ΔE ≥ 13 from the white map in every vision type), so there's no near-invisible first bin. Then come reef blue `#0A70C2` → ultraviolet `#4A3AD8`/`#9A4CF0` → orchid → fuchsia → hot pink `#F52F86` → coral `#FF6347` → tangerine `#FF7A1F` → amber `#F59E00` → burnt amber `#C46A00` → deep plum-wine cap `#5E0F4E`. The top now gets darker instead of paler, because pale gold disappeared on white.
- **500 mb anomaly:** cyan troughs go from ice `#D3F0FA` to deep navy-teal `#021A30`, and fuchsia ridges go from blush `#FFFAFD` to deep plum `#360531`. Near-normal is nearly white; the extremes are deep and saturated.
- **850 mb anomaly:** ultraviolet cold goes from `#F2EFFE` to indigo `#160A4A`, and ember warm goes from peach `#FFF3E8` through orange to dark ember-brown `#421602`. Near-normal is nearly white.
- Still no green, no rainbow, and no blue-white-red (the pairs are cyan/fuchsia and violet/ember).
- **QA** (`qa_cvd_product_scales_light_v1.txt`, all pass):

| Scale | Weakest neighbor pair (any vision type) | Extra check |
|---|---|---|
| Jet / wind10 | 8.1 | First bin vs white ≥ 13.4 |
| 500 mb anomaly | 5.5 | Near-zero split ≥ 7.1 |
| 850 mb anomaly | 5.9 | Near-zero split ≥ 5.9 |

**Mocks:** `mocks/*_aurora_light_v1.png`, superseded by `mocks/*_aurora_light_v2.png` (knot barbs and thicker lines). The dark snow comparison is the existing `mocks/nbm_norcal_passes_snow_deep_ocean_v1.png` (v7 scale, unchanged).

## Wind barbs and line weights (Benjamin 11-03-26 ~4:14 PM PST: "knots symbols that accurately reflect the wind speed… make map lines thicker")
**Barb standard (all maps with barbs):**
- **Units:** knots, from m/s × 1.94384, rounded to the nearest 5 kt.
- **Glyphs:** half feather = 5 kt, full feather = 10 kt, pennant = 50 kt, and an empty circle when calm (under 2.5 kt). The staff points toward where the wind comes from.
- **Data and rotation:** raw model grid points only, never interpolated. GFS 0.25° u/v are earth-relative, and each barb is rotated into the map projection by projecting a tiny step along the true wind. Don't rely on cartopy's `transform_vectors`, which skews earth-relative winds by up to about 8° (see `BARB_SPOTCHECK_v2.md`).
- **Spacing:** 6° on Whole Pacific maps; 4° latitude on North America (Lambert), with the longitude step widened by 1/cos(lat). Regional views get about 1 barb per 90 px.
- **Clearance:** barbs are dropped within 16 px of town labels, H/L markers, jet tags and contour labels, and where the level is below ground.
- **Look:** dark ink `#1A2430`, 1.15 px, length 6.4, with a white 2.6 px halo on the light base.
- **Legend in the footer:** "Barbs: knots · half = 5, full = 10, flag = 50 · circle = calm".
- **Which maps:** 300 mb jet (300 mb wind), 500 mb anomaly (500 mb wind), 850 mb anomaly (850 mb wind), and MSLP + 10 m wind (10 m wind; a no-barb version is also offered).
- **Jet colorbar:** now knots, 50–190 kt, to match the barbs (v1 was 60–220 mph). Jet-core tags are in knots too.
- **10 m wind colorbar:** stays in mph for the general audience, and the footer says "colors = mph". Benjamin can choose knots instead.

**Line-weight rule (light base, 2100 px wide at 100 dpi; values in px):**

| Line | v1 | v2 |
|---|---|---|
| Coastlines | 0.7–0.8 | 1.5 |
| Country borders | 0.6 | 1.2 |
| State/province lines | 0.35 (alpha 0.7) | 0.85 (alpha 0.95) |
| Isobars and height contours | 1.1, halo 2.6 | 1.8, halo 3.8 |
| 32 °F line | 1.8, halo 3.4 | 2.8, halo 4.8 |
| Graticule | 0.5 (alpha 0.22–0.6) | 0.9 (alpha 0.35–0.6) |
| Below-ground outline | 0.8 | 1.3 |
| Map frame | 1.0 | 1.5 |

Colors are unchanged: gray `#8C98A3` for geography and near-black `#1A2733` for contours. Geography stays thinner and lighter than the data contours, so the weather reads first.

## 500 mb height anomaly v3 scale (Benjamin 11-03-26 ~4:20 PM PST: "I don't like the 500mb height anomaly at all… make it look a bit different [from mine] but not a ton color wise")
This replaces the cyan/fuchsia 500 mb anomaly scale on the light base. It lives in `product_scales_light_v3.py` as `H500_ANOM_M`, was built with `h500_scale_build_v3.py`, and is rendered by `render_gfs_products_light_v3.py`.
- **Same logic as his current site:** meters vs the 1991–2020 NCEP/NCAR monthly mean, −450…+450 m in 12 m bins, a flat near-white band for |anomaly| < 18 m, and arrows beyond ±450 m. A cool family sits below normal and a warm family above, with a smooth gradient and the lightest colors at both extremes. Heights are drawn every 6 dam in near-black with a halo, plus 500 mb knot barbs and the v2 line weights.
- **Shifted hues (moderate, not a redesign):**

| Part of scale | His current site | New site |
|---|---|---|
| Strongest lows | Neutral grays | Slate-blue grays |
| Lows | Greens | Teal/jade |
| Approaching normal (below) | Indigo, then royal blue, then light blue | Deep indigo-violet, then ultraviolet, cyan-azure and sky |
| Near normal | Warm white `#f7f7f5` | Cool white `#f8f9fb` |
| Above normal | Pale yellow → orange → red → crimson → magenta | Apricot cream → amber → tangerine → vermilion → rose-red → deep raspberry → plum-magenta |
| Strongest highs | Pink, mauve, light purple | Orchid, pink, blush |

- **How different it is:** the mean CIELAB distance from his scale is 21 per bin (2 at the near-white band, up to 40). All of our anchors are our own; his hexes were used only to build the comparison strip (`mocks/h500_anom_scale_compare_v3.png`). Nothing of his is copied into the new site.
- **"No green" exception:** the guideline is waived for this one scale (teal family), at Benjamin's request to keep a similar feel.
- **Anchors:** slate `#f4f7fa #b3bfce #64778f`; teal `#04302f #0c6660 #1c958c #6fd0c2 #dcf9f2`; violet/blue `#2a1a7a #4a3ad6 #1898dc #a9dcf9`; neutral `#f8f9fb`; warm `#fff4d2 #ffcf55 #ffa424 #f2701c #dc3f22 #c81f3c #8a0f3c #93166f #bb35a3 #df6cc4 #efa6d8 #fbe3ef`. The bins between anchors are spaced evenly by the worst-case color-blind step.
- **Under / over:** `#d6e4f4` / `#f0cde6`.
- **Color-blind QA** (`qa_cvd_product_scales_light_v3.txt`):
  - At 36 m steps (every third bin, outward from normal) it **passes in all four vision types**: normal 14.9, deutan 12.6, protan 12.6, tritan 9.7.
  - At every single 12 m bin it passes only for normal vision (about 5.0). The weakest neighbor pairs are 4.1 (deutan), 4.0 (protan) and 3.1 (tritan).
  - Why it can't pass at every 12 m bin: 36 bins per side at ΔE ≥ 5 would need a worst-case color path of about 180 per side. A smooth one-way gradient on white has only about 70 L* of lightness to work with, and color-blind vision collapses most of the hue changes. Getting there would mean zigzagging the lightness, which would break the smooth look he asked for.
  - For comparison, his current scale scores 1.4–3.9 per bin and deutan 3.2 at 36 m.
  - Recommendation: accept the 36 m pass. The key labels every 90 m, and readers judge the map by bands.

## Reference-look anomaly maps v1 (Benjamin 11-03-26 ~4:42 PM PST: "Mimic these ... but slightly change the colors and if you need to, slightly lighter or darker")
Scope (Benjamin, 4:43 PM PST): only **500 mb height anomaly** and **850 mb temperature anomaly**. No 300/700/850-height maps. The v3 500 mb scale (`H500_ANOM_M`) is untouched.
- **Look borrowed from his reference SLP image (color and feel only):** a smooth diverging banded fill, with the blue family below normal, the orange-red family above, near-white at normal, and thin dark labeled contours. No logo, text, box-and-whisker overlays or layout were taken from it.
- **Ours:** white base, knot barbs (500 / 850 mb wind), v2 line weights. Heights every 6 dam on the 500 mb map; the 32 °F line, signed town values and the gray below-ground mask on the 850 mb map. Same GFS 12Z Nov 3 F024 data and NOAA PSL R1 1991–2020 baseline.
- **Files:**
  - Scales: `product_scales_ref_style_v1.py` (`H500_ANOM_REF`, `T850_ANOM_REF`, one shared 26-color list)
  - Maps: `render_anom_ref_style_v1.py`
  - Strip: `render_anom_scale_vs_reference_v1.py`
  - Mocks: `mocks/gfs_pacific_h500_anom_ref_style_v1.png`, `mocks/gfs_na_t850_anom_ref_style_v1.png`, `mocks/anom_scale_vs_reference_v1.png`
- **Bins:**

| Map | Range | Step | Bins |
|---|---|---|---|
| 500 mb height anomaly | −240…+240 m | 20 m | 12 per side, arrows beyond |
| 850 mb temperature anomaly | −24…+24 °F | 2 °F | 12 per side, arrows beyond |

  These ranges cover this run's extremes (500 mb −216/+231 m, 850 mb −26/+28 °F), so the maps use the full palette. The fine bands keep the gradient smooth.
- **Palette** (under, 12 cold bins from strong to near-normal, 12 warm bins from near-normal to strong, over): `#071a40 #0f3477 #15438d #1b52a2 #2765b5 #3477c6 #478ad2 #629edb #78afe3 #97c0e8 #b1d1ed #cce0f2 #e9f1f8 | #fdefe5 #fdd9c1 #fcc5a3 #fbae83 #f79665 #f17b4d #e6613b #d1422e #b52e2b #991d2b #7b1529 #5e0f26 #3a0a1a`. These are built from our own anchors (cold `#e9f1f8 #b6d4ee #74ade2 #3a82cf #1d58aa #0f3477`; warm `#fdefe5 #fcc9a8 #f89a68 #ec6a3f #cc3b2b #93192b #5e0f26`) and spaced evenly by the worst-case color-blind step.
- **Shift vs the reference:**
  - Blues are a little brighter and more azure through the middle, and the deep end is a lighter cobalt-navy.
  - The warm side leans orange/vermilion in the middle (the reference is pinker-red), and the deep end is a darker wine.
  - Near-normal is split into a cool white (below) and a warm blush (above).
  - Mean CIELAB difference from the reference bands is 13 (range 3 to 24), so it reads as related but not identical. The reference hexes were sampled only for the comparison strip.
- **Guideline waiver:** "no blue-white-red" is waived for these two scales, at Benjamin's request.
- **Color-blind QA** (`qa_cvd_product_scales_ref_style_v1.txt`): **every neighboring pair passes** (minimum neighbor ΔE is normal 6.8, deutan 6.5, protan 6.8, tritan 6.9). The near-zero split is 9.9 or more.
- **Barb spot-check** (`BARB_SPOTCHECK_ref_style_v1.md`): all six sampled barbs are correct, within 0.15° of the true direction.
- **Readability note:** the dark barbs are harder to read on the darkest red bands (+20 °F and above). Options are white barbs over dark bands, or lightening the top 2 bins.

## Per-product specs (core)
**1. 300 mb jet.** Fill uses the wind family at 60–220 mph (14 bins plus an over bin). Heights are drawn every 12 dam as dark lines with a pale halo, smoothed σ 3. Up to 4 jet-core speed tags, at least 2500 km apart and only for cores ≥ 150 mph. No barbs or arrows. Pacific and North America views at 0.25°.
**2. 500 mb anomaly.** v3: the `H500_ANOM_M` scale (meters, −450…+450 every 12; see the section above), with heights every 6 dam on top. Earlier versions used −30…+30 dam every 3 (cyan/fuchsia). No H/L letters. The footer gives the barb legend and the baseline.
**3. 850 mb anomaly.** Fill runs −30…+30 °F every 3 (diverging). The 32 °F (0 °C) line is white with a dark halo and labeled. Where 850 mb is below ground (surface pressure < 850 mb), a flat gray veil covers the map, with no terrain shading. Town values are shown as signed degrees. The full-rectangle Lambert frame is fixed in v2.
**4. MSLP + 10 m wind.** Fill uses the wind family at 10–120 mph, with isobars every 4 mb (2 mb on regional views) using the MSLP v2 line style. H and L letters sit on a pale halo, with pressure-center detection per MSLP v2. "Centers" over terrain where surface pressure is below 950 mb are skipped. Barbs are optional: sparse (every 6°), only where wind is ≥ 10 mph, in mph (half = 5, full = 10, flag = 50), thin pale ink. Never arrows. Mocks are provided with and without barbs.
**5. 500 mb + vorticity.** Absolute vorticity is filled from 16 to 40 ×10⁻⁵ s⁻¹ (transparent below), using a warm half of the wind family. Heights every 6 dam.
**6–11.** Same frame/key/header system. QPF/IVT/snow level use the planned ramps above. Snow uses v7. Temp and gusts use the approved looks.

**Uncrowded rules (all products):** one fill plus one contour set per map (two only on 850 mb). Every contour gets an inline label, but labels that touch towns, H/L markers or the frame are dropped. At most about 8 towns on Pacific and North America views. Tags must sit ≥ 2500 km apart. No graticule labels. The key goes under the map with ≤ 8 ticks at phone width. Credits on the image only when legally required.

## Legal flags
1. **NCEP/NCAR R1 climatology (NOAA PSL):** public domain, no on-image credit. This is a new source, **so it needs Benjamin's OK**. PSL *asks* for an acknowledgment, which goes on the credits page.
2. **ECMWF IFS/AIFS open data:** CC BY 4.0. Any image using it must carry the full ECMWF credit text (rule 5). The GFS-only mocks carry none.
3. **ERA5 / CFSR:** not used. Both need sign-in accounts (rule 1), and ERA5 adds a credit.
4. **OISST and GFS-Wave:** public domain (NOAA), but these are new sources. Verify the terms pages and log them before use (rule 7).
5. **Palettes:** original Aurora Reef colors, checked against the survey's avoid list. No other site's color tables, images, code or branding were copied (new rule 11).
6. **Vorticity/anomaly derived fields** are our own computation. Don't present them as official NOAA products (rule 8).


## Reference-look v2: moved away from the generic WeatherBell-style look (Tue Nov 3, 2026)
- **Why:** Benjamin asked us to make sure these maps don't look too much like WeatherBell. The details are in `WEATHERBELL_COMPARISON_v1.md`.
  - The verdict: v1 shared the generic blue-white-red anomaly look, so v2 pushes further away while keeping the reference feel.
- **Scale:** `product_scales_ref_style_v2.py`.
  - 500 mb: −300…+300 m in 25 m bands.
  - 850 mb: −24…+24°F in 2°F bands.
  - Both use a pure-white near-normal band (±1 step), an indigo-violet cold end and a plum-burgundy warm end with more orange in the middle.
  - Built from our own anchors only.
- **CVD QA** (`qa_cvd_product_scales_ref_style_v2.txt`): minimum neighbor ΔE is 9.0 normal, 7.8 deutan, 6.7 protan and 7.6 tritan. All pass (the line is 5).
- **Map style** (`render_anom_ref_style_v2.py`):
  - Navy-charcoal contours with labels on white chips.
  - White barbs with a dark halo where the fill under the barb is dark (L* < 45). This fixes the 850 mb dark-barb issue.
  - Knots throughout.
  - The barb spot-check is in `BARB_SPOTCHECK_ref_style_v2.md`: all Δangle within 0.2° and speeds exact.
- **Mocks:** `mocks/gfs_pacific_h500_anom_ref_style_v2.png` (2100×1842) and `mocks/gfs_na_t850_anom_ref_style_v2.png` (2100×1306), plus the strip `mocks/anom_scale_ref_style_v1_vs_v2.png` (2100×520). The v1 files are unchanged.

## Decisions for Benjamin
1. Light base for most products, dark for snow, pass views, radar and clouds (table above): OK?
2. 2 m temp: keep the approved dark look, or retune it for light?
3. Aurora Reef Light colors: keep or adjust?
4. New 500 mb anomaly scale (v3): OK, a bit closer to his, or a bit further?
5. Reference-look anomaly maps (500 mb, 850 mb temp): use v2 (more distinct from WeatherBell-style maps) instead of v1 / v3 / Aurora, or keep options?
6. Barbs on MSLP + wind: sparse barbs or no barbs?
7. 10 m wind colors: keep mph, or switch to knots to match the barbs?
8. Anomaly baseline: OK to use NOAA PSL Reanalysis 1 (1991–2020)?
9. Switch that baseline to its daily means (sharper)?
10. Core list: OK, or add/remove?
11. Jet: 300 mb only, or add 250 mb?
12. Waves and SST at launch, or later?

## Reference-look v3: brighter grey-purple low end (Tue Nov 3, 2026 ~6:15 PM PST)
- **Why:** Benjamin asked, "Could we possibly make the lower end of the scale a brighter greyish purple?"
- **Scale:** `product_scales_ref_style_v3.py`. Same as v2 except the four strongest below-normal bands and the "under" arrow.
  - The new grey-purples, from the extreme in toward normal: under #bfaed6, then #a993c8, #9479b9, #7d61aa and #684c9c.
  - 500 mb: under −300 m, then −300…−200 m. 850 mb: under −24°F, then −24…−16°F.
  - They get lighter outward from the darkest cobalt band (#3a68cd), so they stay separate from the blues for color-blind viewers.
  - Not like WeatherBell's gray/green/blue lows.
- **CVD QA** (`qa_cvd_product_scales_ref_style_v3.txt`):
  - Minimum neighbor ΔE: 9.6 normal, 7.8 deutan, 6.7 protan, 7.6 tritan (pass).
  - Purple to cobalt step: 16.7 or more.
  - Purples vs the non-adjacent light blues and white: 6.7 or more (protan is the tightest).
- **Renderer:** `render_anom_ref_style_v3.py`, the v2 renderer with the v3 scale. The barb check passes (`BARB_SPOTCHECK_ref_style_v3.md`).
  - The grey-purples are light, so barbs on them are drawn dark; the white outlined barbs remain on the dark warm bands.
- **Mocks:** `mocks/gfs_pacific_h500_anom_ref_style_v3.png` (2100×1842) and `mocks/gfs_na_t850_anom_ref_style_v3.png` (2100×1306), plus the strip `mocks/anom_scale_ref_style_v2_vs_v3.png` (2100×520). The v1 and v2 files are unchanged.

## CANONICAL anomaly scale: v4 `anom_scale.py` / `anom_scale.json` (Tue Nov 3, 2026 ~6:20 PM PST)
- **Why:** Benjamin approved the v3 look and said, "smooth out the scale with triple the transitions in colors and that's what you'll build into the site."
- **What it is:** this is the single anomaly scale the site uses for the 500 mb height anomaly and the 850 mb temperature anomaly. v1–v3 are history only.
- **How it's built:** each v3 band is split into 3.
  - Fine band 3k is exactly v3 band k, and the next two step toward the next v3 color in OKLab.
  - That gives 72 bands plus under and over: 74 colors, 73 edges.
- **Bands:** 500 mb runs −300…+300 m in 8.33 m steps. 850 mb runs −24…+24°F in 0.67°F steps.
  - The white near-normal band stays ±25 m / ±2°F (6 fine bands).
  - Colorbar ticks stay at the old round values.
- **For the site:** `anom_scale.json`. colors[0] = under, colors[-1] = over, and colors[i] fills edges[i-1]..edges[i].
- **CVD QA** (`qa_cvd_anom_scale.txt`):
  - Neighbor steps fall below the strict 5 line (min 2.1–3.1). That's expected for a gradient, so it does NOT meet the strict neighbor pass.
  - Every 3rd band (one old step) passes: 9.6 normal, 7.7 deutan, 6.1 protan, 7.0 tritan. White to the first color is 12.1 or more.
- **Mocks:** `mocks/gfs_pacific_h500_anom_ref_style_v4.png` (2100×1842), `mocks/gfs_na_t850_anom_ref_style_v4.png` (2100×1306) and the strip `mocks/anom_scale_ref_style_v3_vs_v4.png` (2100×360).
  - The renderer is `render_anom_ref_style_v4.py` (v3 plus anom_scale). Contours, barbs, white outlined barbs on dark bands and line weights are unchanged.

## Canonical anomaly scale v5: straight grey bottom (Tue Nov 3, 2026 ~6:30 PM PST)
- **Why:** Benjamin said, "Make straight grey be at the ... bottom of the anomaly scale."
- **How I read it:** the lowest end now ends in neutral grey #aaaaaa (R=G=B). The rest of the scale is identical to v4.
  - The under arrow and the strongest band (−300…−291.7 m / −24…−23.3°F) are #aaaaaa.
  - The next band is #a99fba, a blend toward the v4 grey-purples.
- **Files:** `anom_scale.py` / `anom_scale.json` now say version 5. v4 is frozen as `anom_scale_v4.py` / `.json`, and the v4 scripts now import the frozen copy.
- **CVD QA** (`qa_cvd_anom_scale.txt`):
  - Neighbor steps are below the strict 5 line (min 2.1–3.1, as in v4).
  - Every 3rd band passes: 9.6 normal, 7.7 deutan, 6.1 protan, 7.0 tritan.
  - Grey vs #a993c8: 31.1 normal, 24.2 deutan, 26.8 protan, 8.6 tritan.
  - Grey vs white and the pale blues: 21.2 or more.
  - Grey vs the 850 mb below-ground veil #C3CAD1: about 12 in every view. The veil also has an outline and a "Below ground" label.
- **Barbs on grey:** dark barbs, contrast 6.8:1. Today's run doesn't reach the grey (lows about −220 m), so the maps show no grey yet.
- **Mocks:** `mocks/gfs_pacific_h500_anom_ref_style_v5.png` (2100×1842), `mocks/gfs_na_t850_anom_ref_style_v5.png` (2100×1306) and the strip `mocks/anom_scale_ref_style_v4_vs_v5.png` (2100×360).

## 850 mb products v6: high terrain filled, ±1°F white, more contrast (Tue Nov 3, 2026 ~7:20 PM PST)
- **RULE: never blank high terrain on 850 mb products.**
  - Fill everywhere, using the 850 mb values exactly as GFS provides them below ground.
  - Mark high terrain only with a thin dotted outline (surface pressure < 850 mb).
  - Keep the footnote "values there are GFS's extrapolated values (*)" and add an asterisk on town values there.
  - No barbs below ground.
- **Where the terrain values come from:** GFS 0.25° pgrb2 has TMP 850 at every grid point. NCEP extrapolates it below ground, and this run has zero missing points.
  - We don't extrapolate or fill anything ourselves.
  - The R1 1991–2020 climatology is also defined everywhere, so the anomaly is defined everywhere too.
- **Polish:** Gaussian smoothing σ = 1.6 grid points (~40 km), then 3× bicubic upsampling before the fill, so there's no speckle.
  - The 32°F line is now drawn over terrain as well, and town values replace the "Below ground" labels.
- **Canonical `anom_scale.py` / `.json` v6:** the 850 mb anomaly now has its own edges and colors. 500 mb is unchanged.
  - White band −1…+1°F, then 33 bands per side from 1 to 24°F (0.697°F steps): 69 colors, 68 edges.
  - Contrast boost: OKLab chroma ×1.35 (gamut-aware, no neon primaries) plus a slight darkening near normal.
  - v5 is frozen as `anom_scale_v5.py` / `.json`.
  - QA (`qa_cvd_anom_scale.txt`):
    - Neighbor mean ΔE is 6.4 / 5.7 / 5.4 / 5.2 (normal / deutan / protan / tritan), up from v5's 5.3 / 4.8 / 4.6 / 4.6.
    - Neighbor min is 2.0–3.2, below the strict line.
    - Every-3rd min is 11.8 / 7.6 / 5.4 / 6.7 (pass).
    - White to the ±1°F colors: 16.3–23.0.
- **New 850 mb temperature scale** `temp850_scale.py` (original): −40…+80°F in 2°F bands, 62 colors.
  - Cold side: violet → indigo → azure → sky → ice up to 32°F. Warm side: pale lemon → marigold → tangerine → vermilion → wine.
  - Each side is spaced by the worst-case color-blind step.
  - QA (`qa_cvd_temp850_scale.txt`):
    - Neighbor min 1.7–2.4 (below 5).
    - Every 3rd (6°F) min 8.1 / 6.0 / 7.1 / 5.2 (pass).
    - The step at 32°F is 16 or more in every view.
- **Mocks:** `mocks/gfs_na_t850_anom_ref_style_v6.png` and `mocks/gfs_na_t850_temp_v1.png`, both 2100×1306. Renderer `render_t850_v6.py`; barb check in `BARB_SPOTCHECK_t850_v6.md`.

## Site theme: "Coastal Daylight" proposed (Tue Nov 3, 2026 ~8:20 PM PST)
- The details are in `THEME_PROPOSAL.md`, which has the ranked list of 19 products and their status.
- **The look:** white land, sea-glass ocean, navy ink, teal accent, Atkinson Hyperlegible (OFL), a time tile on the left of the header, a vertical capsule key on the right, and H/L as filled discs.
- **Samples:** `mocks/theme_cd_t2m_pnw_v1.png` and `mocks/theme_cd_mslp_precip_pnw_v1.png` (each 2100×1400), plus the board `mocks/theme_board_v1.png` (2400×1700).
- **Status:** step 1 only; the other products wait for Benjamin's OK on the theme.

## Wave products, Coastal Daylight theme v1 mocks (Tue Nov 3, 2026 ~9:45 PM PST)
- **Data:** ECMWF IFS HRES-WAM 0.25° open data, CC BY 4.0. 12Z Tue Nov 3 run (4 AM PST), F276, valid Sat Nov 14 4 PM PST (00Z Sun Nov 15).
  - Open-data steps checked for this run: 240, 270, 276 and 360 h all exist, so the exact F276 was used.
  - No hmax field exists, so max wave = 1.86 × swh (Rayleigh), stated on the map.
- **Variant:** the light theme with warm off-white land #F6F4EF so the sea fill reads, plus navy tile header, capsule key on the right and Atkinson Hyperlegible.
- **Scales** (original, our own anchors, spaced with path_cvd):
  - Max wave: 0–85 ft in 18 bands (0, 3, 6, 10, 15 … 85), going pale ice → cerulean → teal → lime → gold → orange → vermilion → raspberry → plum → violet → orchid → pink, with an over color.
  - Hs: 0–50 ft in 18 bands (0, 1, 2, 3, 4, 6 … 50).
  - QA is in `qa_cvd_wave_scales_v1.txt`.
- **Hs map:** mean wave direction arrows point toward where the waves travel, evenly thinned. Arrows are white on dark bands and navy elsewhere. Dashed lines show peak period at 14 and 18 s.
- **Mocks:**
  - `mocks/theme_cd_wave_max_nepac_v1.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_nepac_v1.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_pnw_v1.png` (2100×1360)
- **Not used:** NDBC buoys (a new source, pending approval).

## Wave products v2, night mode (Tue Nov 3, 2026 ~9:55 PM PST)
- **Fixes and changes** (Benjamin t71u, t73u–t76u):
  - The maps are upright: Mercator with central meridian −140 (NE Pacific) and −127 (PNW). v1's Lambert projection with a −145 meridian had tilted the coast.
  - Night mode: navy canvas #0A1626, light text #E8F0F7, slate land #2B3647, a teal-outlined time tile, and no white anywhere.
  - Scales are 3× smoother: 54 bands each, interpolated in OKLab, with round tick labels kept.
  - Base colors nudged so the smooth bands pass the every-3rd check:
    - Max wave: #3f69ab → #545d90.
    - Hs: #3e69ac → #00407a and #edcd42 → #d3e550.
  - Max wave map: no in-map value chips. Plain bottom-right text "Maximum wave height: N ft", using the maximum in view (88 ft for this run).
- **QA** (`qa_cvd_wave_scales_v2.txt`):
  - Neighbor steps are below the strict line (max wave 2.4–3.8; Hs 2.9–4.4 for color-blind views, 5.1 for normal vision).
  - Every 3rd band passes everywhere: max wave ≥ 5.9, Hs ≥ 5.6. The 18 base bands pass (≥ 8.8).
  - Every scale color is ≥ 11.4 from the slate land.
- **Mocks:**
  - `mocks/theme_cd_wave_max_nepac_night_v2.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_nepac_night_v2.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_pnw_night_v2.png` (2100×1360)
  - v1 is unchanged.

## Wave products night v3 (Tue Nov 3, 2026 ~10:05 PM PST)
- **Changes** (Benjamin t77u–t82u):
  - 36 bands per scale, 2× the 18 base colors. Same anchors and nudges as v2.
  - "Maximum wave height: 88 ft" moved inside the map at the bottom right (3.5% above the map edge): Atkinson Bold 29, white with a dark soft halo and drop shadow. It's no longer in the footer.
  - Direction arrows about 62% of the v2 size and slightly denser (2.1° spacing on the NE Pacific map, 0.68° on the PNW map).
  - Borders about 2×: country 2.4 #A9BACB, state 1.7 #8C9DB0. Coastline unchanged.
- **QA** (`qa_cvd_wave_scales_v3.txt`):
  - Neighbor steps: max wave 4.6–5.9 (normal and deutan pass the strict line; protan and tritan just under). Hs 5.0–7.9 (normal, deutan and protan pass; tritan 5.0 is borderline).
  - Every 3rd band passes on both scales (≥ 5.6).
  - Every 2nd band (one original color step apart) passes everywhere except one Hs protan window at 3.9.
- **Mocks:**
  - `mocks/theme_cd_wave_max_nepac_night_v3.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_nepac_night_v3.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_pnw_night_v3.png` (2100×1360)
  - `mocks/wave_band_compare_v3.png` (2100×816): 18 / 36 / 54 bands, same crop.

## Wave products v4: light base map, black surround (Tue Nov 3, 2026 ~10:15 PM PST)
- **Changes** (Benjamin t80u/t81u):
  - Inside the map: light warm off-white land #F6F4EF, coastline #4E5D6E, borders country 2.4 #5b6b7d and state 1.7 #7f8da0.
  - Outside the map: header, footer and key area on near-black #05080d with light text. There's no white margin anywhere.
  - Everything else is the same as night v3.
- **QA:** the scale numbers are the same as v3 (`qa_cvd_wave_scales_v4.txt`).
  - The lowest-wave colors are fairly close to the light land (smallest 4.5 for Hs protan), but the dark coastline separates them.
- **Mocks:**
  - `mocks/theme_cd_wave_max_nepac_v4.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_nepac_v4.png` (2100×1720)
  - `mocks/theme_cd_wave_hs_dir_pnw_v4.png` (2100×1360)
  - `mocks/wave_page_preview_v4.png` (1920×1470): the max wave map on a black webpage.
  - `mocks/wave_band_compare_v4.png` (2100×816)
- **Rule for the wave maps:** a light base map inside the graphic, and near-black for the page and graphic surround.
