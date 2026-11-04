# Design brief: PNW · California · Hawaii model site

Prepared Tue Nov 3, 2026 (PST) for Benjamin. Three directions to pick from, or mix (for example, one direction's UI with another's scales). Nothing is built until you pick.

**Mocks are real data:** GFS 0.25°, run Tue Nov 3, 2026 4:00 AM PST (12Z), F012, valid Tue Nov 3, 2026 4:00 PM PST. Source: NOAA GFS on AWS open data (`noaa-gfs-bdp-pds`, no sign-in), fields PRMSL and TMP 2 m pulled by byte range. Basemap: Natural Earth (10m for California, 50m for the Pacific). Figure 16 in × 100 dpi = 1600 px wide, full size.

| Direction | Mode | CA temperature mock | Whole-Pacific MSLP mock | All color keys |
|---|---|---|---|---|
| Deep Ocean Night | dark | `mocks/deep_ocean_ca_temp.png` | `mocks/deep_ocean_pacific_mslp.png` | `mocks/deep_ocean_keys.png` |
| Coastal Fog | light | `mocks/coastal_fog_ca_temp.png` | `mocks/coastal_fog_pacific_mslp.png` | `mocks/coastal_fog_keys.png` |
| Basalt & Ember | dark, warm | `mocks/basalt_ca_temp.png` | `mocks/basalt_pacific_mslp.png` | `mocks/basalt_keys.png` |

Single source of truth: `style_draft.py` (every palette, bin, font and map color as data). `STYLE_RULES_DRAFT.md` lists every scale bin-by-bin with hex values and is generated from it (`make_style_rules.py`), so the two can't drift. Color-blind check: `qa_cvd.py` → `qa_cvd_report.txt`.

All palettes are original to this project: built from fresh anchors (several hand-tuned in CIELAB for even lightness steps), not taken from the current site, from other bots' files on this box, or from any other weather site.

---

## What's shared by all three

These stay the same whichever direction you pick, so models and views stay consistent.

- **Units:** °F, inches, mph, mb, ft, s, dBZ, J/kg, dam. Same as the current site.
- **Bins (same for all directions):**
  - **2 m temperature:** 2 °F bands from −30 to 120 °F. The cold and warm ramps are separate, with a hard break at **32 °F**: color and lightness both jump there. Every temperature map also gets a labeled 32 °F contour, and on the key the 32 tick is bold, in the accent color, with a divider line.
  - **Precip/QPF (in):** 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10+.
  - **Snow (in):** 0.1, 0.5, 1, 2, 3, 4, 6, 8, 12, 18, 24, 36, 48, 72+.
  - **Wind/gusts (mph):** 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120+. Below 10 mph is not drawn.
  - **MSLP (mb):** fill from 960 to 1050 in 2 mb steps. Isobars every 4 mb, bold every 20 mb, labels every 8 mb.
  - **MSLP anomaly (mb):** −40 to +40 in 4 mb steps, diverging around 0.
  - **Waves (ft):** 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40+ (significant, max and swell height).
  - **Wave/swell period (s):** 4 to 22 in 2 s steps.
  - **Composite reflectivity (dBZ):** 5 to 75 in 5 dBZ steps.
  - **CAPE (J/kg):** 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000+.
  - **500 mb anomaly (dam):** −30 to +30 in 3 dam steps, diverging around 0.
- **Color order logic:**
  - Sequential scales (precip, snow, wind, waves, CAPE) run light/quiet to dark/intense, then flip to a bright "extreme" color at the top bin so the rare high end stands out.
  - Diverging scales (both anomalies) use opposite hue families that stay apart for color-blind viewers: blue vs coral, teal vs gold, purple vs green, or teal vs lava.
  - Reflectivity has a deliberate hue jump at 30–35 dBZ, where convective cores start.
- **Color-blind readability:** every neighboring bin pair is at least ΔE 5 (CIE76) apart under normal vision and simulated deuteranopia, protanopia and tritanopia (Machado 2009). This passes for all 33 scales. Temperature is checked at 10 °F steps and MSLP at 10 mb steps. Across the 32 °F break, ΔE is 15 to 89 depending on direction and vision type.
- **Keys:**
  - Horizontal, under the map, at about 62% of the width.
  - Extend arrows match the scale (both ends on temperature and MSLP; top end only on precip and snow).
  - Desktop shows every 10 °F plus 32. On a 375 px phone, the key drops to at most 8 labels (`ticks_375`). For temperature that's −20, 0, 20, 32, 50, 70, 90, 110.
  - Tick labels use the map-label font at weight 500; the key title and units use the UI font at 600.
- **Header:**
  - Panel strip with a 2.5 px accent rule along the bottom.
  - Product title in the heading font.
  - "GFS 0.25° · Run <PT time> (<Z>) · F0xx" in the muted UI font.
  - Valid time (PT) in an accent pill badge on the right.
- **Footer credit line on every map:** "Data: NOAA (public domain) · Basemap: Natural Earth". ECMWF maps add "Data: ECMWF, CC BY 4.0".
- **Town labels:**
  - Dot plus name, and the value on scalar maps (for example "Fresno 71°").
  - Label font semibold, 14 pt at 1600 px, with a 3.5 px halo.
  - Each town has a fixed side.
  - If an H/L marker lands on a town dot, the marker lifts so it clears the town's label. On the mock this happens at Tokyo with the 1031 mb high.
- **H/L markers:** circle badge with the letter in the heading font and the central pressure under it.
  - Found on smoothed MSLP (σ 4 grid points) in a ~10° window, with at least 2 mb of prominence.
  - Kept at least 30 px inside the frame, so none are cut off at the edges.
  - H/L detection and contour smoothing are stronger on large frames (Pacific, North America) and lighter on tight views.
- **Dateline:** the Pacific view uses `Mercator(central_longitude=180)` with data kept on one continuous 110°E–90°W strip (shifted −180° into the 180-centred frame), so there's no seam at 180°. A faint 20° graticule runs through 180° in all three mocks to show that.
- **Lines on filled maps:** coastlines, state and country lines switch to a dark "fill_line" color on full-cover fills like temperature, so they stay visible over every band. On basemap-only areas they use the direction's coast color.

---

## 1. Deep Ocean Night (`deep_ocean`)

**Mood:** Calm, nocturnal, instrument-panel dark: midnight water, sea-glass teal, buoy-light amber.

- **Mode:** dark.
- **UI palette:**
  - bg: `#0B1622`
  - panel: `#122233`
  - panel2: `#1A2E44`
  - line: `#2A4460`
  - text: `#E6EEF5`
  - muted: `#8FA3B8`
  - accent: `#3FD0C9`
  - accent2: `#F2B84B`
- **Fonts** (all SIL Open Font License 1.1, verified from `OFL.txt` in the google/fonts repo, downloaded to `fonts/`):
  - **Headings:** Space Grotesk 700 (Florian Karsten).
  - **UI:** IBM Plex Sans 400/600 (IBM; Reserved Font Name "Plex").
  - **Map labels:** IBM Plex Sans Condensed 500/600.
- **Map styling:**
  - **Land and ocean:** land `#1E2B37` (slate), ocean `#0D1B29` (midnight).
  - **Lines:** coastline `#C9D7E3`, 0.8 px, over the basemap; on temperature fills, lines go dark `#0B1622`.
  - **Towns:** sea-glass dots with white text and a navy halo.
  - **H/L markers:** H amber `#F2B84B`, L sky `#5FB6FF`.
  - **Isobars and contours:** isobars near-white `#E9F1F7`, 0.9 px (1.6 px major); the 32 °F line is white.
- **Scales:**
  - **Temperature:** cold side runs pale lilac → violet → indigo → bright blue at 31 °F. Warm side starts with a jump to deep sea-green at 32 °F, then runs green → lime → gold → orange → red → wine, with a pink glow at 115 °F and up.
  - **Precip:** sea-foam → teal → blue → violet → magenta → coral → pale peach at the top.
  - **Snow:** ice blue → periwinkle → violet → orchid pink.
  - **Wind:** dim teal → green → yellow → orange → red → plum, with lilac at 120+.
  - **MSLP:** deep blue (lows) → teal → sage → sand (highs).
  - **MSLP anomaly:** periwinkle (negative) vs coral (positive), with a dark center.
  - **500 mb anomaly:** teal (troughs) vs gold (ridges), with a dark center.
  - **Waves:** navy → teal → mint → yellow → coral → plum, with pale lilac at 40 ft and up.
  - **Period:** indigo → cyan → pale yellow.
  - **Reflectivity:** slate-teal → green → yellow → orange → red → magenta → lavender.
  - **CAPE:** dark teal → olive-yellow → orange → crimson → violet.

## 2. Coastal Fog (`coastal_fog`)

**Mood:** Bright, editorial, print-chart light: marine-layer paper, harbor blue ink, lighthouse red-orange.

- **Mode:** light. Good outdoors and on phones in daylight, and it reads like a printed chart.
- **UI palette:**
  - bg: `#F4F1EA`
  - panel: `#FFFFFF`
  - panel2: `#E8E4DA`
  - line: `#CFC8B8`
  - text: `#1E2A2F`
  - muted: `#5E6B70`
  - accent: `#C9472D`
  - accent2: `#2F6F8F`
- **Fonts** (all SIL OFL 1.1, verified, downloaded):
  - **Headings:** Fraunces 600 (Undercase Type; soft serif).
  - **UI:** Public Sans 400/600 (USWDS).
  - **Map labels:** Atkinson Hyperlegible 400/700 (Braille Institute; designed for low-vision legibility).
- **Map styling:**
  - **Land and ocean:** land `#D3CCBA` (warm putty), ocean `#DCE6EA` (fog blue).
  - **Lines:** coastline and borders in charcoal ink `#26343A`.
  - **Towns:** lighthouse-red dots, near-black text with a paper halo.
  - **H/L markers:** H harbor blue, L lighthouse red (traditional chart colors).
  - **Isobars and contours:** isobars charcoal 0.85 px (1.5 px major) with paper-colored label halos; the 32 °F line is charcoal.
- **Scales:**
  - **Temperature:** cold side runs deep navy → harbor blue → pale ice at 31 °F. Warm side jumps to sage green at 32 °F, then runs pale straw (about 50 °F) → gold → orange → rust → crimson-brown → deep plum at 120 °F.
  - **Precip:** pale green → teal → blue → indigo → plum → rose.
  - **Snow:** white-blue → periwinkle → violet → burgundy.
  - **Wind:** pale sage → teal → navy → plum → brick → orange.
  - **MSLP:** soft blue (lows) → paper → tan (highs).
  - **MSLP anomaly:** blue vs rust, with a paper-white center.
  - **500 mb anomaly:** purple vs green, with a paper-white center.
  - **Waves:** white-aqua → blue → violet → brick → orange.
  - **Period:** straw → sage → slate → indigo.
  - **Reflectivity:** sea-green (light echoes) → hue jump to yellow at 30 dBZ → orange → red → purple.
  - **CAPE:** straw → yellow → orange → red → violet.

## 3. Basalt & Ember (`basalt`)

**Mood:** Warm, bold, volcanic dark: cooled lava rock, glowing ember orange, fresh-fern green.

- **Mode:** dark, warm-tinted (brown-black rather than blue-black).
- **UI palette:**
  - bg: `#16120F`
  - panel: `#221B17`
  - panel2: `#2E2520`
  - line: `#4A3C33`
  - text: `#F1E7DC`
  - muted: `#A8988A`
  - accent: `#FF6A3D`
  - accent2: `#7CC6B0`
- **Fonts** (all SIL OFL 1.1, verified, downloaded):
  - **Headings:** Sora 700 (geometric, bold).
  - **UI:** Manrope 400/700.
  - **Map labels:** Barlow Semi Condensed 500/600, which fits more labels per view.
- **Map styling:**
  - **Land and ocean:** land `#2A231E` (basalt), ocean `#141C1F`.
  - **Lines:** coastline cream `#E8DCCD`.
  - **Towns:** ember-orange dots with cream text.
  - **H/L markers:** H ember `#FF8A5C`, L fern `#7CC6B0`.
  - **Isobars and contours:** isobars cream 0.9 px (1.6 px major); the 32 °F line is cream.
- **Scales:**
  - **Temperature:** cold side runs pale glacier → sky → steel blue → dark indigo at 31 °F. Warm side jumps to pale fern at 32 °F (the strongest break of the three), then runs green → olive → gold → orange → lava red → oxblood → near-black at 120 °F.
  - **Precip:** pale green → teal → indigo → magenta → coral → gold.
  - **Snow:** white → blue → violet → wine.
  - **Wind:** ash → sage → yellow → orange → lava → oxblood, with blush at 120+.
  - **MSLP:** dusky indigo (lows) → ash gray → warm rose-sand (highs).
  - **MSLP anomaly:** teal vs lava, with a dark center.
  - **500 mb anomaly:** blue vs amber, with a dark center.
  - **Waves:** slate → teal → green → yellow → orange → red, with blush at 40 ft and up.
  - **Period:** violet → teal → pale yellow.
  - **Reflectivity:** ash-green → yellow → orange → red → magenta → orchid.
  - **CAPE:** moss → olive → orange → red → plum → orchid.

---

## Licenses and assets

| Font | Role | License | Source | Local files |
|---|---|---|---|---|
| Space Grotesk | heading (1) | SIL OFL 1.1 | github.com/google/fonts `ofl/spacegrotesk` | `fonts/space-grotesk/` |
| IBM Plex Sans / Condensed | UI, labels (1) | SIL OFL 1.1, Reserved Font Name "Plex" | `ofl/ibmplexsans`, `ofl/ibmplexsanscondensed` | `fonts/ibm-plex-sans*/` |
| Fraunces | heading (2) | SIL OFL 1.1 | `ofl/fraunces` | `fonts/fraunces/` |
| Public Sans | UI (2) | SIL OFL 1.1 | `ofl/publicsans` | `fonts/public-sans/` |
| Atkinson Hyperlegible | labels (2) | SIL OFL 1.1 | `ofl/atkinsonhyperlegible` | `fonts/atkinson-hyperlegible/` |
| Sora | heading (3) | SIL OFL 1.1 | `ofl/sora` | `fonts/sora/` |
| Manrope | UI (3) | SIL OFL 1.1 | `ofl/manrope` | `fonts/manrope/` |
| Barlow Semi Condensed | labels (3) | SIL OFL 1.1 | `ofl/barlowsemicondensed` | `fonts/barlow-semi-condensed/` |

- Each font folder has a static TTF (used for the PNG renders), a latin-subset WOFF2 for the web (Google Fonts' own subset, fetched through google-webfonts-helper) and `OFL.txt`.
- **Plex note:** if we subset Plex further ourselves, OFL's Reserved Font Name rule means the modified file can't be called "Plex". Either keep Google's WOFF2 unchanged or rename the family in the subset.
- **Data and basemap:** NOAA GFS (public domain) and Natural Earth (public domain; credited anyway as required).

## Decisions for Benjamin

1. **Pick a direction**, or a mix, for example "Coastal Fog UI with Deep Ocean scales".
2. **Optional light/dark toggle:** Coastal Fog could ship as a light theme next to one of the dark ones. The bins stay identical; only colors swap.
3. **More regional views later?** The starter brief suggests SoCal, Bay Area, Oregon coast and a Big Island close-up.
4. **Mountain-pass and summit-road cards:** which Cascades and Siskiyou passes, Donner/Tioga/Tejon, and the Haleakalā and Mauna Kea roads should be included?

## Known limits of the mocks

- These are static matplotlib renders of the style. The real site colors the maps in the browser, using the same scale data.
- The 32 °F contour is lightly smoothed, so on the California map it can sit a few pixels off the fill edge.
- Some isobar labels (for example "1016") can land partly on the frame edge; the browser renderer will place labels away from the edges.
- On this run, the only sub-32 °F areas on the California map are the high Sierra at 4 PM PST, so the cold half of the temperature scale shows up mainly on the key sheets (`mocks/*_keys.png`).
