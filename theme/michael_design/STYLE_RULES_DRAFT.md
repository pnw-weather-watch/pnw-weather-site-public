# STYLE_RULES_DRAFT.md

Draft rules for the PNW / California / Hawaii model site. Generated from `style_draft.py` by `make_style_rules.py`. Nothing here is final until Benjamin picks a direction; the pick becomes `style.py` + `STYLE_RULES.md`.

## Shared rules (all directions)

- Units: °F, inches, mph, mb, ft, s, dBZ, J/kg, dam (same as the current site).
- Bins are shared by every direction and every model; only colors change per direction.
- Below the first bin of precip, snow, wind, waves, reflectivity and CAPE is transparent (not drawn).
- 2 m temperature: 2 °F bands from −30 to 120 °F, two separate ramps with a hard break at 32 °F (cold ramp ends, warm ramp starts with a jump in hue *and* lightness). A 32 °F contour is drawn on every temperature map, labeled “32°F”; the 32 tick is bold and accent-colored on the key, with a full-height divider.
- MSLP: fill in 2 mb steps (960–1050), isobars every 4 mb, bold every 20 mb (1000, 1020, 1040), labels every 8 mb. Smoothing: Gaussian σ 3 grid points on Pacific/North America, σ 1–1.5 on tight views.
- H/L: local max/min of σ 4 smoothed MSLP in a 41-point (≈10°) window, prominence ≥ 2 mb, must sit ≥ 30 px inside the frame. Glyph is a circle badge (heading font) with the central pressure below. If a marker sits on a town dot, the marker is lifted 34 pt so the town label stays readable.
- Town labels: dot + name + value (on scalar maps), label font semibold 14 pt at 1600 px wide, 3.5 px halo in the town-halo color, fixed side per town (see `TOWNS`).
- California city points (v2, Benjamin 11-03-26): every city is plotted at its official airport ASOS/METAR site from `ca_airports.csv` (lat/lon from api.weather.gov station metadata), and the number is the model 2 m value bilinearly interpolated to that airport point, not the city center. Labels are “City 64°”, semibold 13 pt; each station has a fixed preferred side (`render_v2.PREF`), dense clusters (LA basin, Bay Area) use short callouts with a haloed leader line; labels never overlap each other, a dot or the frame edge.
- Keys: horizontal under the map. Desktop shows `ticks`; at ≤ 480 px wide (375 px phone) use `ticks_375` (≤ 8 labels). Extend arrows follow `extend`.
- Credits on every map: “Data: NOAA (public domain)” and “Basemap: Natural Earth” (add “Data: ECMWF, CC BY 4.0” on ECMWF maps).
- All times in the header are Pacific Time with PST/PDT label; run time also shows the Z cycle.
- Color-blind QA: `qa_cvd.py` checks CIE76 ΔE between neighboring bins under normal, deuteranopia, protanopia and tritanopia (Machado 2009). Pass = every neighbor ΔE ≥ 5 (temperature checked at 10 °F steps, MSLP at 10 mb steps). All 33 scales pass; see `qa_cvd_report.txt`.

## Bins

| Scale | Unit | Edges | Extend | Phone ticks (375 px) |
|---|---|---|---|---|
| 2 m temperature | °F | -30 to 120 every 2 | both | -20, 0, 20, 32, 50, 70, 90, 110 |
| Precipitation / QPF | in | 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10 | max | 0.1, 0.5, 1, 2, 4, 8 |
| Snowfall | in | 0.1, 0.5, 1, 2, 3, 4, 6, 8, 12, 18, 24, 36, 48, 72 | max | 1, 3, 6, 12, 24, 48 |
| Wind and gusts (10 m, 850/500/250 mb wind) | mph | 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120 | max | 10, 20, 30, 40, 50, 70, 90, 120 |
| MSLP fill (isobars drawn on top) | mb | 960 to 1050 every 2 | both | 960, 980, 1000, 1020, 1040 |
| MSLP anomaly | mb | -40, -36, -32, -28, -24, -20, -16, -12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | both | -40, -24, -8, 8, 24, 40 |
| Wave height (sig., max, swell) | ft | 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40 | max | 2, 4, 6, 10, 15, 25, 40 |
| Wave / swell period | s | 4, 6, 8, 10, 12, 14, 16, 18, 20, 22 | both | 4, 8, 12, 16, 20 |
| Composite reflectivity | dBZ | 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75 | max | 10, 20, 30, 40, 50, 60, 70 |
| CAPE (SB/MU) | J/kg | 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000 | max | 250, 1000, 2000, 3000, 5000 |
| 500 mb height anomaly | dam | -30, -27, -24, -21, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30 | both | -30, -18, -6, 6, 18, 30 |

## Direction: Deep Ocean Night (`deep_ocean`)

*Calm, nocturnal, instrument-panel dark: midnight water, sea-glass teal, buoy-light amber.* Mode: dark.

UI: bg `#0B1622`, panel `#122233`, panel2 `#1A2E44`, line `#2A4460`, text `#E6EEF5`, muted `#8FA3B8`, accent `#3FD0C9`, accent2 `#F2B84B`

Map: land `#1E2B37`, ocean `#0D1B29`, coast `#C9D7E3`, coast_w `0.8`, border `#9DB2C6`, border_w `0.6`, lake `#0D1B29`, town_text `#F4F8FB`, town_halo `#06101A`, town_dot `#3FD0C9`, hi `#F2B84B`, lo `#5FB6FF`, isobar `#E9F1F7`, isobar_w `0.9`, isobar_major_w `1.6`, freeze_line `#FFFFFF`, contour_label_bg `None`, graticule `#2A4460`, fill_line `#0B1622`, isobar_v2 `#0A1420`, isobar_v2_w `1.25`, isobar_v2_halo `#EAF3F8`, isobar_v2_halo_w `2.4`, isobar_v2_halo_alpha `0.55`, isobar_v2_label_size `11.5`, isobar_v2_label_halo `3.2`, isobar_v2_every `4`, hi_v2 `#2335B8`, lo_v2 `#E02450`, hl_v2_halo `#F4F8FB`, hl_v2_size `25`, hl_v2_halo_w `3.0`, hl_v2_value_size `10.5`, hl_v2_value_offset `-19`, hl_v2_value_halo `2.0`, mslp_fill_lines `#0A1420`

Fonts: heading: Space Grotesk 700; ui: IBM Plex Sans regular; ui_bold: IBM Plex Sans 600; label: IBM Plex Sans Condensed 500; label_bold: IBM Plex Sans Condensed 600

### 2 m temperature

Cold ramp anchors: -30°F `#EEE2FA`, -15°F `#C6A0EA`, 0°F `#9064D6`, 10°F `#6141B4`, 20°F `#3048A8`, 27°F `#2B6CC2`, 32°F `#64AEEA`

Warm ramp anchors: 32°F `#1F7D6C`, 42°F `#3FA27A`, 52°F `#94C46C`, 60°F `#DCD65A`, 70°F `#F3B444`, 80°F `#EC8233`, 90°F `#D44E2A`, 100°F `#A82334`, 110°F `#6B0E35`, 120°F `#F2C6DC`

Sample bands: -35°F `#eee2fa`, -29°F `#ebdef9`, -19°F `#d1b2ee`, -9°F `#b088e2`, 1°F `#8b60d2`, 11°F `#5c42b3`, 21°F `#2f4eac`, 31°F `#59a1e2`, 31°F `#59a1e2`, 33°F `#22806d`, 41°F `#3c9e79`, 51°F `#8bc06d`, 61°F `#ded358`, 71°F `#f2af42`, 81°F `#e97c32`, 91°F `#cf492b`, 101°F `#a22134`, 111°F `#792146`, 125°F `#f2c6dc`

### Precipitation / QPF (in)

| Bin | Color |
|---|---|
| 0.01–0.05 | `#b5e6df` |
| 0.05–0.1 | `#79cfc9` |
| 0.1–0.25 | `#42afba` |
| 0.25–0.5 | `#2d88b1` |
| 0.5–0.75 | `#3063a8` |
| 0.75–1 | `#3f4195` |
| 1–1.5 | `#54257a` |
| 1.5–2 | `#882e8a` |
| 2–3 | `#b63e82` |
| 3–4 | `#da5f7c` |
| 4–6 | `#ee8981` |
| 6–8 | `#f8b699` |
| 8–10 | `#fddec1` |
| ≥ 10 | `#fff6ea` |

### Snowfall (in)

| Bin | Color |
|---|---|
| 0.1–0.5 | `#e4eef8` |
| 0.5–1 | `#c0d5ed` |
| 1–2 | `#99b8e0` |
| 2–3 | `#729bd3` |
| 3–4 | `#577dc3` |
| 4–6 | `#4c5db0` |
| 6–8 | `#54439c` |
| 8–12 | `#552773` |
| 12–18 | `#853185` |
| 18–24 | `#ad428d` |
| 24–36 | `#cb6099` |
| 36–48 | `#e48db2` |
| 48–72 | `#f4bcd2` |
| ≥ 72 | `#ffe6f0` |

### Wind and gusts (10 m, 850/500/250 mb wind) (mph)

| Bin | Color |
|---|---|
| 10–15 | `#2a5a6a` |
| 15–20 | `#2e7982` |
| 20–25 | `#379894` |
| 25–30 | `#56b49a` |
| 30–35 | `#8ccd95` |
| 35–40 | `#c4da88` |
| 40–45 | `#edd876` |
| 45–50 | `#f7b85a` |
| 50–60 | `#f39249` |
| 60–70 | `#e76940` |
| 70–80 | `#d04644` |
| 80–90 | `#ae2d4f` |
| 90–100 | `#892159` |
| 100–120 | `#7e3475` |
| ≥ 120 | `#e4c6f0` |

### MSLP fill (isobars drawn on top)

Bins (this direction): 900 to 1060 mb every 2, extend both; key ticks every 10 mb.

Anchors (low → high): 900 mb `#061028`, 915 mb `#0F1B4C`, 930 mb `#30206B`, 945 mb `#4E2687`, 958 mb `#4240A4`, 968 mb `#005ABB`, 977 mb `#006FCC`, 985 mb `#0085CC`, 992 mb `#009DCD`, 998 mb `#00B4C4`, 1003 mb `#2FC2A0`, 1007 mb `#4ECB8A`, 1011 mb `#8FD7A8`, 1015 mb `#D6E2DC`, 1018 mb `#EDE8D2`, 1021 mb `#F5DDA0`, 1024 mb `#F4C670`, 1028 mb `#F2A94E`, 1032 mb `#E98A47`, 1036 mb `#DD6A4C`, 1040 mb `#CB4C5A`, 1044 mb `#AE3566`, 1048 mb `#86276A`, 1054 mb `#5E1C5C`, 1060 mb `#3C1240`

Sample bands: 901 mb `#07112a`, 911 mb `#0d1842`, 921 mb `#1c1d58`, 931 mb `#32206d`, 941 mb `#46247f`, 951 mb `#483294`, 961 mb `#2e48ab`, 971 mb `#0061c1`, 981 mb `#007acc`, 991 mb `#009acd`, 1001 mb `#1dbdae`, 1011 mb `#90d7a9`, 1021 mb `#f5dd9f`, 1031 mb `#eb9149`, 1041 mb `#c3465d`, 1051 mb `#712163`

#### MSLP v2 rules (Benjamin 11-03-26 11:40 AM PT: “closer to mine with some color differences”)

- Structure follows Benjamin's current site; colors are Deep Ocean's own. Low → high: near-black navy (900) > deep navy > violet (930-945) > blue-violet (958) > cobalt and azure (968-992) > cyan/aqua (~998) > jade and mint greens (1003-1011, no lime) > cool fog-gray neutral (~1015) > pale sand (1018) > buoy amber (1024) > copper (1032) > coral-rose (1040) > plum-wine > deep plum (1060). His site uses lime greens, a cream neutral and brick/dark reds at the top; this one does not.
- Fill covers land and sea (no land tint), smoothed σ 1.5 grid points. Coastlines, borders and state lines are dark (`mslp_fill_lines` `#0A1420`) on top; faint dotted graticule every 20° (dateline visible, no seam).
- Isobars: every 4 mb on Pacific / continental views (2 mb on regional views), dark `#0A1420` 1.25 px on a soft pale halo `#EAF3F8` 2.4 px at 0.55 opacity, smoothed σ 3. Every isobar is labeled inline, label font semibold 11.5 pt in the isobar color on a pale halo. No bold/major isobars. Labels that touch an H/L marker, a town label or the frame edge are removed.
- H/L: bold letter in the heading font, 25 pt at 1600 px wide, H `#2335B8` (indigo-blue), L `#E02450` (crimson-rose), pale halo `#F4F8FB` 3.0 px; no circle badge. Central pressure (whole mb) in the same color, semibold 10.5 pt, 19 pt below the letter.
- H/L detection: extremum of σ 3 smoothed MSLP within 800 km, at least 3 mb above/below the median of the ring at 800 km, one center per 800 km; must sit ≥ 22 px inside the frame. If a marker touches a town dot or label it is nudged 26-40 pt up or down.

### MSLP anomaly (mb)

| Bin | Color |
|---|---|
| < -40 | `#efeeff` |
| -40–-36 | `#dbdbff` |
| -36–-32 | `#c6c9ff` |
| -32–-28 | `#b0b5fd` |
| -28–-24 | `#9aa2f9` |
| -24–-20 | `#858fed` |
| -20–-16 | `#707cdd` |
| -16–-12 | `#616bc7` |
| -12–-8 | `#525bad` |
| -8–-4 | `#444c8f` |
| -4–0 | `#47426e` |
| 0–4 | `#633c44` |
| 4–8 | `#803f37` |
| 8–12 | `#9e483d` |
| 12–16 | `#ba5345` |
| 16–20 | `#d5604d` |
| 20–24 | `#e9755e` |
| 24–28 | `#f78b71` |
| 28–32 | `#fca48c` |
| 32–36 | `#ffbda8` |
| 36–40 | `#ffd4c5` |
| ≥ 40 | `#ffebe2` |

### Wave height (sig., max, swell) (ft)

| Bin | Color |
|---|---|
| 1–2 | `#173b5b` |
| 2–3 | `#1c5777` |
| 3–4 | `#1f7790` |
| 4–5 | `#2896a0` |
| 5–6 | `#44b1a6` |
| 6–8 | `#79c9a3` |
| 8–10 | `#b4db9f` |
| 10–12 | `#e2e39a` |
| 12–15 | `#f5c779` |
| 15–20 | `#f29b5c` |
| 20–25 | `#e26d4d` |
| 25–30 | `#c44552` |
| 30–40 | `#9d3368` |
| ≥ 40 | `#e9d3f5` |

### Wave / swell period (s)

| Bin | Color |
|---|---|
| < 4 | `#2c2a6b` |
| 4–6 | `#383a8a` |
| 6–8 | `#3d52a3` |
| 8–10 | `#3e6cb3` |
| 10–12 | `#4189bd` |
| 12–14 | `#4aa4bf` |
| 14–16 | `#62bcb9` |
| 16–18 | `#87d0b2` |
| 18–20 | `#a9daa3` |
| 20–22 | `#cde2a2` |
| ≥ 22 | `#fff8da` |

### Composite reflectivity (dBZ)

| Bin | Color |
|---|---|
| 5–10 | `#2e4a5a` |
| 10–15 | `#3d6b76` |
| 15–20 | `#4c8f8c` |
| 20–25 | `#66b498` |
| 25–30 | `#98d190` |
| 30–35 | `#d0dd80` |
| 35–40 | `#efce62` |
| 40–45 | `#f4a644` |
| 45–50 | `#eb7a35` |
| 50–55 | `#da4d31` |
| 55–60 | `#bf2b40` |
| 60–65 | `#9f2269` |
| 65–70 | `#913a9b` |
| 70–75 | `#bc87dc` |
| ≥ 75 | `#f0e2ff` |

### CAPE (SB/MU) (J/kg)

| Bin | Color |
|---|---|
| 100–250 | `#1f4e5f` |
| 250–500 | `#2a7370` |
| 500–750 | `#4a9a72` |
| 750–1000 | `#8cb76a` |
| 1000–1500 | `#d2c95e` |
| 1500–2000 | `#f0a74a` |
| 2000–2500 | `#ea7a3f` |
| 2500–3000 | `#d74e45` |
| 3000–4000 | `#b6345a` |
| 4000–5000 | `#8d2c75` |
| ≥ 5000 | `#d9a6e8` |

### 500 mb height anomaly (dam)

| Bin | Color |
|---|---|
| < -30 | `#d5fbfb` |
| -30–-27 | `#abeeed` |
| -27–-24 | `#82e0df` |
| -24–-21 | `#61ced0` |
| -21–-18 | `#42bcc1` |
| -18–-15 | `#2fa9b0` |
| -15–-12 | `#1f949e` |
| -12–-9 | `#17818c` |
| -9–-6 | `#156e7b` |
| -6–-3 | `#1d5c68` |
| -3–0 | `#304f52` |
| 0–3 | `#534835` |
| 3–6 | `#6e4e29` |
| 6–9 | `#855d2a` |
| 9–12 | `#9b6c2b` |
| 12–15 | `#b27c2c` |
| 15–18 | `#c68f36` |
| 18–21 | `#d8a242` |
| 21–24 | `#e5b65e` |
| 24–27 | `#f2cb7c` |
| 27–30 | `#f9dea2` |
| ≥ 30 | `#fff2c9` |

## Direction: Coastal Fog (`coastal_fog`)

*Bright, editorial, print-chart light: marine-layer paper, harbor blue ink, lighthouse red-orange.* Mode: light.

UI: bg `#F4F1EA`, panel `#FFFFFF`, panel2 `#E8E4DA`, line `#CFC8B8`, text `#1E2A2F`, muted `#5E6B70`, accent `#C9472D`, accent2 `#2F6F8F`

Map: land `#D3CCBA`, ocean `#DCE6EA`, coast `#26343A`, coast_w `0.8`, border `#4B5A60`, border_w `0.55`, lake `#DCE6EA`, town_text `#141C20`, town_halo `#FBFAF6`, town_dot `#C9472D`, hi `#2F6F8F`, lo `#C9472D`, isobar `#2A363B`, isobar_w `0.85`, isobar_major_w `1.5`, freeze_line `#1E2A2F`, contour_label_bg `#FBFAF6`, graticule `#C3CDD1`, fill_line `#1E2A2F`

Fonts: heading: Fraunces 600; ui: Public Sans regular; ui_bold: Public Sans 600; label: Atkinson Hyperlegible regular; label_bold: Atkinson Hyperlegible 700

### 2 m temperature

Cold ramp anchors: -30°F `#0F2E3A`, -15°F `#1D4E6B`, 0°F `#2D6E9E`, 12°F `#4A8DC6`, 22°F `#7FB2DF`, 32°F `#CFE3F3`

Warm ramp anchors: 32°F `#93BF93`, 42°F `#BFD79A`, 52°F `#E9E3A0`, 60°F `#F0CC78`, 70°F `#E6A659`, 80°F `#D47846`, 90°F `#B64E40`, 100°F `#8C2E49`, 110°F `#5D1F53`, 120°F `#36163F`

Sample bands: -35°F `#0f2e3a`, -29°F `#10303d`, -19°F `#19455e`, -9°F `#235b7f`, 1°F `#3071a2`, 11°F `#488ac3`, 21°F `#7aafdd`, 31°F `#c7def1`, 31°F `#c7def1`, 33°F `#97c194`, 41°F `#bad499`, 51°F `#e5e29f`, 61°F `#efc875`, 71°F `#e4a257`, 81°F `#d17345`, 91°F `#b24b41`, 101°F `#872c4a`, 111°F `#591e51`, 125°F `#36163f`

### Precipitation / QPF (in)

| Bin | Color |
|---|---|
| 0.01–0.05 | `#e3f0d4` |
| 0.05–0.1 | `#c3e2b4` |
| 0.1–0.25 | `#97ce9e` |
| 0.25–0.5 | `#69b69a` |
| 0.5–0.75 | `#499a99` |
| 0.75–1 | `#377b95` |
| 1–1.5 | `#335d8e` |
| 1.5–2 | `#313d74` |
| 2–3 | `#4e2964` |
| 3–4 | `#7d2b71` |
| 4–6 | `#822561` |
| 6–8 | `#a6375b` |
| 8–10 | `#c96167` |
| ≥ 10 | `#e39a8a` |

### Snowfall (in)

| Bin | Color |
|---|---|
| 0.1–0.5 | `#eef1f6` |
| 0.5–1 | `#d7deed` |
| 1–2 | `#bbc8e2` |
| 2–3 | `#9db0d6` |
| 3–4 | `#8197c9` |
| 4–6 | `#6a7cbb` |
| 6–8 | `#5b64ab` |
| 8–12 | `#56519a` |
| 12–18 | `#594088` |
| 18–24 | `#623375` |
| 24–36 | `#6f2a64` |
| 36–48 | `#7e2954` |
| 48–72 | `#91304a` |
| ≥ 72 | `#a63f45` |

### Wind and gusts (10 m, 850/500/250 mb wind) (mph)

| Bin | Color |
|---|---|
| 10–15 | `#e6eedd` |
| 15–20 | `#cae0c3` |
| 20–25 | `#a9cdad` |
| 25–30 | `#83b79e` |
| 30–35 | `#609d92` |
| 35–40 | `#49848a` |
| 40–45 | `#3e6a84` |
| 45–50 | `#3e517b` |
| 50–60 | `#322d5e` |
| 60–70 | `#6e3169` |
| 70–80 | `#883065` |
| 80–90 | `#9b3357` |
| 90–100 | `#b7454a` |
| 100–120 | `#cf643f` |
| ≥ 120 | `#e08d3c` |

### MSLP fill (isobars drawn on top)

Anchors (low → high): `#7FA2C9`, `#9BB8D7`, `#B7CDE2`, `#D0DFE9`, `#E6EDEC`, `#F3EEDF`, `#F0DFC4`, `#E8CBA6`, `#DDB389`, `#CF9A6E`

Sample bands: 961 mb `#84a6cb`, 971 mb `#a0bbd9`, 981 mb `#bbd0e3`, 991 mb `#d3e1e9`, 1001 mb `#e7edeb`, 1011 mb `#f3eddd`, 1021 mb `#efdec2`, 1031 mb `#e7caa4`, 1041 mb `#dcb288`

### MSLP anomaly (mb)

| Bin | Color |
|---|---|
| < -40 | `#1f4d7a` |
| -40–-36 | `#2c5e8f` |
| -36–-32 | `#386fa3` |
| -32–-28 | `#4c81b3` |
| -28–-24 | `#6093c2` |
| -24–-20 | `#79a5ce` |
| -20–-16 | `#95b9da` |
| -16–-12 | `#aec9e3` |
| -12–-8 | `#c5d9eb` |
| -8–-4 | `#d9e5ee` |
| -4–0 | `#ebeeee` |
| 0–4 | `#f4ede3` |
| 4–8 | `#f4e2ce` |
| 8–12 | `#f1d5b7` |
| 12–16 | `#ebc39e` |
| 16–20 | `#e5b085` |
| 20–24 | `#db9a6a` |
| 24–28 | `#d28552` |
| 28–32 | `#c4713f` |
| 32–36 | `#b55e2e` |
| 36–40 | `#a14f24` |
| ≥ 40 | `#8c3f1a` |

### Wave height (sig., max, swell) (ft)

| Bin | Color |
|---|---|
| 1–2 | `#e6f1f4` |
| 2–3 | `#c4e2ea` |
| 3–4 | `#98ccdd` |
| 4–5 | `#6bb3cf` |
| 5–6 | `#4c96c0` |
| 6–8 | `#3f75ae` |
| 8–10 | `#43579a` |
| 10–12 | `#4d3f86` |
| 12–15 | `#5e2e72` |
| 15–20 | `#78265c` |
| 20–25 | `#93304b` |
| 25–30 | `#b34a3f` |
| 30–40 | `#d1703a` |
| ≥ 40 | `#e59b47` |

### Wave / swell period (s)

| Bin | Color |
|---|---|
| < 4 | `#f3e9c9` |
| 4–6 | `#e1dba9` |
| 6–8 | `#c5cb93` |
| 8–10 | `#a3bb88` |
| 10–12 | `#7fa885` |
| 12–14 | `#5e9585` |
| 14–16 | `#487f85` |
| 16–18 | `#3b6982` |
| 18–20 | `#35537b` |
| 20–22 | `#343d70` |
| ≥ 22 | `#352a60` |

### Composite reflectivity (dBZ)

| Bin | Color |
|---|---|
| 5–10 | `#d8e8e0` |
| 10–15 | `#add5c4` |
| 15–20 | `#7dbfab` |
| 20–25 | `#56a495` |
| 25–30 | `#408789` |
| 30–35 | `#aab574` |
| 35–40 | `#e8c159` |
| 40–45 | `#e49d43` |
| 45–50 | `#d97736` |
| 50–55 | `#c6532e` |
| 55–60 | `#a9342e` |
| 60–65 | `#86223b` |
| 65–70 | `#6b2159` |
| 70–75 | `#5f3384` |
| ≥ 75 | `#9b7cc4` |

### CAPE (SB/MU) (J/kg)

| Bin | Color |
|---|---|
| 100–250 | `#eef0d8` |
| 250–500 | `#d9e3b1` |
| 500–750 | `#bfd48c` |
| 750–1000 | `#e8d06b` |
| 1000–1500 | `#efb252` |
| 1500–2000 | `#ea8d45` |
| 2000–2500 | `#dc6a43` |
| 2500–3000 | `#c54b4a` |
| 3000–4000 | `#a83457` |
| 4000–5000 | `#832c66` |
| ≥ 5000 | `#5e2a6e` |

### 500 mb height anomaly (dam)

| Bin | Color |
|---|---|
| < -30 | `#3d2466` |
| -30–-27 | `#4d3279` |
| -27–-24 | `#5c408d` |
| -24–-21 | `#70549f` |
| -21–-18 | `#8568b1` |
| -18–-15 | `#9a7ec1` |
| -15–-12 | `#b196d1` |
| -12–-9 | `#c0a8dd` |
| -9–-6 | `#ceb8e6` |
| -6–-3 | `#ddcdec` |
| -3–0 | `#eee7ef` |
| 0–3 | `#e7efe0` |
| 3–6 | `#cbe4c0` |
| 6–9 | `#b2d8a6` |
| 9–12 | `#9dcc96` |
| 12–15 | `#88c086` |
| 15–18 | `#70b078` |
| 18–21 | `#5aa16b` |
| 21–24 | `#468f5e` |
| 24–27 | `#337d50` |
| 27–30 | `#276a43` |
| ≥ 30 | `#1a5736` |

## Direction: Basalt & Ember (`basalt`)

*Warm, bold, volcanic dark: cooled lava rock, glowing ember orange, fresh-fern green.* Mode: dark (warm).

UI: bg `#16120F`, panel `#221B17`, panel2 `#2E2520`, line `#4A3C33`, text `#F1E7DC`, muted `#A8988A`, accent `#FF6A3D`, accent2 `#7CC6B0`

Map: land `#2A231E`, ocean `#141C1F`, coast `#E8DCCD`, coast_w `0.8`, border `#B3A392`, border_w `0.55`, lake `#141C1F`, town_text `#FFF6EC`, town_halo `#120D0A`, town_dot `#FF6A3D`, hi `#FF8A5C`, lo `#7CC6B0`, isobar `#F5ECE2`, isobar_w `0.9`, isobar_major_w `1.6`, freeze_line `#FFF6EC`, contour_label_bg `None`, graticule `#3A302A`, fill_line `#120D0A`

Fonts: heading: Sora 700; ui: Manrope regular; ui_bold: Manrope 700; label: Barlow Semi Condensed 500; label_bold: Barlow Semi Condensed 600

### 2 m temperature

Cold ramp anchors: -30°F `#DCEFF2`, -15°F `#9FD1DB`, 0°F `#5FA6C2`, 12°F `#3C76A6`, 22°F `#34508A`, 32°F `#3A3A78`

Warm ramp anchors: 32°F `#B4DBA6`, 42°F `#86BC80`, 52°F `#C3C35C`, 62°F `#EBC24B`, 72°F `#F29A3A`, 82°F `#E5652C`, 92°F `#C23A27`, 102°F `#8C1F24`, 112°F `#55141C`, 120°F `#2E0B10`

Sample bands: -35°F `#dceff2`, -29°F `#d8edf1`, -19°F `#b0d9e1`, -9°F `#85c0d1`, 1°F `#5ca2c0`, 11°F `#3f7aa8`, 21°F `#35538d`, 31°F `#393c7a`, 31°F `#393c7a`, 33°F `#b0d8a3`, 41°F `#8bbf84`, 51°F `#bdc260`, 61°F `#e7c24d`, 71°F `#f19e3c`, 81°F `#e66a2d`, 91°F `#c53e27`, 101°F `#912224`, 111°F `#5a151d`, 125°F `#2e0b10`

### Precipitation / QPF (in)

| Bin | Color |
|---|---|
| 0.01–0.05 | `#e8f4d8` |
| 0.05–0.1 | `#bde3b5` |
| 0.1–0.25 | `#87c99a` |
| 0.25–0.5 | `#54ab8e` |
| 0.5–0.75 | `#358c88` |
| 0.75–1 | `#2d6b86` |
| 1–1.5 | `#344c80` |
| 1.5–2 | `#3e2d6a` |
| 2–3 | `#76307c` |
| 3–4 | `#933072` |
| 4–6 | `#bc4567` |
| 6–8 | `#e06e5c` |
| 8–10 | `#f7a55b` |
| ≥ 10 | `#ffd77a` |

### Snowfall (in)

| Bin | Color |
|---|---|
| 0.1–0.5 | `#f2f4f7` |
| 0.5–1 | `#dae3ed` |
| 1–2 | `#bfcfe4` |
| 2–3 | `#a3bada` |
| 3–4 | `#88a4d1` |
| 4–6 | `#728dc5` |
| 6–8 | `#6675b5` |
| 8–12 | `#635fa5` |
| 12–18 | `#664c93` |
| 18–24 | `#6d3c80` |
| 24–36 | `#78336f` |
| 36–48 | `#873061` |
| 48–72 | `#9b3757` |
| ≥ 72 | `#b4484f` |

### Wind and gusts (10 m, 850/500/250 mb wind) (mph)

| Bin | Color |
|---|---|
| 10–15 | `#4e4740` |
| 15–20 | `#615b53` |
| 20–25 | `#6b6e63` |
| 25–30 | `#778974` |
| 30–35 | `#89a985` |
| 35–40 | `#a4c48e` |
| 40–45 | `#cbd68b` |
| 45–50 | `#edd576` |
| 50–60 | `#f6b85e` |
| 60–70 | `#f6964b` |
| 70–80 | `#ee713d` |
| 80–90 | `#da4d33` |
| 90–100 | `#bb3330` |
| 100–120 | `#a93c44` |
| ≥ 120 | `#f3c1b0` |

### MSLP fill (isobars drawn on top)

Anchors (low → high): `#262755`, `#37365F`, `#494666`, `#5A576B`, `#6B6870`, `#7F7876`, `#9B867D`, `#B89485`, `#D4A28F`, `#EEB29B`, `#FFC4AD`

Sample bands: 961 mb `#292a57`, 971 mb `#3c3b61`, 981 mb `#504d68`, 991 mb `#625f6d`, 1001 mb `#767173`, 1011 mb `#91817b`, 1021 mb `#b19083`, 1031 mb `#d0a08d`, 1041 mb `#ecb19a`

### MSLP anomaly (mb)

| Bin | Color |
|---|---|
| < -40 | `#eefbf4` |
| -40–-36 | `#caebdc` |
| -36–-32 | `#a7dbc4` |
| -32–-28 | `#89ccb4` |
| -28–-24 | `#6cbca4` |
| -24–-20 | `#52a794` |
| -20–-16 | `#3b9182` |
| -16–-12 | `#317a72` |
| -12–-8 | `#2a6663` |
| -8–-4 | `#295454` |
| -4–0 | `#334344` |
| 0–4 | `#51322e` |
| 4–8 | `#6a2d27` |
| 8–12 | `#823228` |
| 12–16 | `#9d3b29` |
| 16–20 | `#bb472b` |
| 20–24 | `#d45b2f` |
| 24–28 | `#e87134` |
| 28–32 | `#f18b4b` |
| 32–36 | `#f8a564` |
| 36–40 | `#fbbe86` |
| ≥ 40 | `#ffd6a8` |

### Wave height (sig., max, swell) (ft)

| Bin | Color |
|---|---|
| 1–2 | `#2c3e4a` |
| 2–3 | `#2e5765` |
| 3–4 | `#31747c` |
| 4–5 | `#3b918a` |
| 5–6 | `#57ab8d` |
| 6–8 | `#86c38b` |
| 8–10 | `#bcd58a` |
| 10–12 | `#e7da80` |
| 12–15 | `#f6bc64` |
| 15–20 | `#f39250` |
| 20–25 | `#e46a44` |
| 25–30 | `#c84641` |
| 30–40 | `#a33543` |
| ≥ 40 | `#f6d5c8` |

### Wave / swell period (s)

| Bin | Color |
|---|---|
| < 4 | `#3a2e5a` |
| 4–6 | `#443c73` |
| 6–8 | `#4a5089` |
| 8–10 | `#4d6699` |
| 10–12 | `#517ea4` |
| 12–14 | `#5b96a8` |
| 14–16 | `#71aca6` |
| 16–18 | `#8dc1a2` |
| 18–20 | `#afd39d` |
| 20–22 | `#d5e39b` |
| ≥ 22 | `#f7eda0` |

### Composite reflectivity (dBZ)

| Bin | Color |
|---|---|
| 5–10 | `#3e4a4a` |
| 10–15 | `#4e6a64` |
| 15–20 | `#5b8977` |
| 20–25 | `#74a682` |
| 25–30 | `#9cc185` |
| 30–35 | `#cad37e` |
| 35–40 | `#ebcc68` |
| 40–45 | `#f5ad4d` |
| 45–50 | `#f0873c` |
| 50–55 | `#e15e34` |
| 55–60 | `#c83b33` |
| 60–65 | `#a62640` |
| 65–70 | `#902b66` |
| 70–75 | `#ac5fae` |
| ≥ 75 | `#e6b8f0` |

### CAPE (SB/MU) (J/kg)

| Bin | Color |
|---|---|
| 100–250 | `#3b4a3e` |
| 250–500 | `#4f6d4e` |
| 500–750 | `#73905a` |
| 750–1000 | `#a4ad5e` |
| 1000–1500 | `#d5c25e` |
| 1500–2000 | `#f1a54a` |
| 2000–2500 | `#ec7e40` |
| 2500–3000 | `#d95540` |
| 3000–4000 | `#b83a4a` |
| 4000–5000 | `#903060` |
| ≥ 5000 | `#e0a5d9` |

### 500 mb height anomaly (dam)

| Bin | Color |
|---|---|
| < -30 | `#d8e6ff` |
| -30–-27 | `#bfd4fa` |
| -27–-24 | `#a5c1f4` |
| -24–-21 | `#8aabe9` |
| -21–-18 | `#6f95de` |
| -18–-15 | `#5a7ece` |
| -15–-12 | `#4767bc` |
| -12–-9 | `#3b54a7` |
| -9–-6 | `#32438d` |
| -6–-3 | `#2d366a` |
| -3–0 | `#322e49` |
| 0–3 | `#452e2a` |
| 3–6 | `#5f361d` |
| 6–9 | `#80451c` |
| 9–12 | `#9f561d` |
| 12–15 | `#bd691f` |
| 15–18 | `#d68025` |
| 18–21 | `#eb972d` |
| 21–24 | `#f4ae49` |
| 24–27 | `#fbc468` |
| 27–30 | `#fdd68e` |
| ≥ 30 | `#ffe8b5` |

## v3 additions (Tue Nov 3, 2026, 12:40 PM PST): snow depth change scale (Deep Ocean Night)

Defined in `style_draft.py` as `SNOW_CHG` / `build_snow_chg()`. Diverging, uniform-width key. Warm = loss, transparent = little or none, blue to white to lavender = gain. CVD check (qa_cvd.py method): minimum neighbour dE 8.1 (protan), 10.0 (normal).

| Bin (in) | Color |
|---|---|
| < -12 | `#8E2F2A` |
| -12 to -6 | `#C8552E` |
| -6 to -3 | `#E0853A` |
| -3 to -1 | `#E9B66A` |
| -1 to 0.1 | transparent (no fill) |
| 0.1–1 | `#2D5B86` |
| 1–3 | `#3A7DB6` |
| 3–6 | `#4C9FD8` |
| 6–12 | `#7BC1EC` |
| 12–18 | `#A9D8F5` |
| 18–24 | `#D6EDFB` |
| 24–36 | `#F7FBFF` |
| 36–48 | `#C8B6F0` |
| ≥ 48 | `#9A7BE0` |

Route markers (v3): Interstate and US route use the public-domain MUTCD SVGs (Wikimedia Commons, license.json ok=true) in `assets/shields/`, copied from the handoff. CA state route = original green miner's-spade drawing (white border, white Overpass 800 numerals, small "CALIFORNIA"); NV state route = white Nevada outline (Natural Earth) on a black square with black numerals. Pass cards = green summit guide sign (white inset border, Overpass caps, "ELEV nnnn"). Road credit wording: "Roads: US Census TIGER".

## v4 update (Tue Nov 3, 2026, 12:41 PM PST): snow depth change scale, current (Deep Ocean Night)

Replaces the v3 gain colors after Benjamin's feedback ("white on the upper end, 48 in plus, purple and pink below that"). Defined in `style_draft.py` as `SNOW_CHG_V4`, built with `build_snow_chg(slug, ver="v4")` (the default stays `"v3"` so the v3 mock reproduces unchanged). Same edges and melt bins as v3. Gain runs light blue (smallest) through blues, indigo and violets to magenta-purple, pink, then white at 48+ in. The white top bin always gets a dark outline (`#06101A`) on chips and legend, the key draws thin dividers between bins, and maps draw a thin dark contour on the 48 in edge so white never blends into pink or into labels. CVD check (`qa_cvd.py`, now includes `snow_chg_v4`): minimum neighbour dE 15.1 normal, 12.2 deutan, 10.5 protan, 14.5 tritan; every gain color vs land `#1E2B37` at least 20.4.

Pass views (v4) also drop terrain relief: flat Deep Ocean Night land (`#1E2B37`) and ocean (`#0D1B29`) fill only, and no relief credit.

| Bin (in) | Color |
|---|---|
| < -12 | `#8E2F2A` |
| -12 to -6 | `#C8552E` |
| -6 to -3 | `#E0853A` |
| -3 to -1 | `#E9B66A` |
| -1 to 0.1 | transparent (no fill) |
| 0.1–1 | `#B4DAF2` light blue |
| 1–3 | `#78B4E4` sky blue |
| 3–6 | `#4688CE` mid blue |
| 6–12 | `#2F5AAE` deep blue |
| 12–18 | `#4532A2` indigo |
| 18–24 | `#7D45C0` violet |
| 24–36 | `#B850C0` magenta-purple |
| 36–48 | `#F49CD4` pink |
| ≥ 48 | `#FFFFFF` white (dark outline) |


## v6 (Tue Nov 3, 2026, 12:52 PM PST): THE site-wide snow scale — use for ALL snow maps

Benjamin, on v5: "Add about double of the amount of transitional colors, and increase the top end to 60 in. Keep the same general scale you created there and that will be the scale for all snow maps on this site."

- **Source of truth:** `snow_scale.py` (Python: `build("change")` for depth-change maps, `build("amount")` for snow depth and snowfall totals) and `snow_scale.json` (same edges and hex colors for the site front end). `style_draft.build_snow_chg(slug, ver="v6")` mirrors it. The old `BINS["snow"]`, `SNOW_CHG` (v3) and `SNOW_CHG_V4` are kept only so older mocks reproduce; don't use them for new work.
- **Applies to:** snow depth change, snow depth, snowfall totals (any model), pass cards and chips, meteogram snow bars. Amount maps use the gain half only (< 0.1 in = no fill, 60+ = white).
- **Hue path:** same as v4/v5 with twice the steps. Gain runs light blue → blues → deep indigo (12–15 in, the darkest step) → violet → purple → magenta → pink → **white at 60+**. Loss (change maps only) runs pale amber → orange → rust → deep red. -1 to +0.1 in = no fill. Colors are CIELAB-interpolated between hand-picked anchors. Lightness falls through the blues to the indigo, then rises steadily to white.
- **White top bin:** always has a dark outline (`#06101A`) on chips and keys, and maps draw a thin dark contour at 60 in.
- **Key:** full width, every edge labeled, thin dividers between bins.
- **CVD check** (`qa_cvd.py`, `snow_chg_v6`): minimum neighbour dE 9.1 normal, 8.1 deutan, 6.9 protan, 6.7 tritan (flag < 5). Gain colors vs land `#1E2B37` ≥ 12.9 (tritan, darkest indigo).
- Bins: 8 loss + no fill + 18 gain + 60+ (was 4 + no fill + 8 + 48+ in v4/v5).

| Bin (in) | Color |
|---|---|
| < -24 | `#5E1A20` |
| -24 to -18 | `#762425` |
| -18 to -12 | `#8E2F2A` |
| -12 to -9 | `#A63F2C` |
| -9 to -6 | `#BF4F2D` |
| -6 to -4.5 | `#CE6832` |
| -4.5 to -3 | `#DC8038` |
| -3 to -2 | `#EAA865` |
| -2 to -1 | `#F3CF92` |
| -1 to 0.1 (no fill) | transparent (no fill) |
| 0.1-0.5 | `#CDE8F9` |
| 0.5-1 | `#B1D7F3` |
| 1-2 | `#93C6EC` |
| 2-3 | `#79B1E3` |
| 3-4.5 | `#5C9CD9` |
| 4.5-6 | `#4C84CD` |
| 6-9 | `#3A6CC0` |
| 9-12 | `#2E4AA6` |
| 12-15 | `#22247C` |
| 15-18 | `#3E2A9C` |
| 18-21 | `#6036B4` |
| 21-24 | `#8444C2` |
| 24-30 | `#A652D0` |
| 30-36 | `#BD60CE` |
| 36-42 | `#D26ECC` |
| 42-48 | `#E084D1` |
| 48-54 | `#EE9AD6` |
| 54-60 | `#F8C6E6` |
| 60+ | `#FFFFFF` (dark outline `#06101A`) |


## v7 (Tue Nov 3, 2026, 12:58 PM PST): THE site-wide snow scale — current, use for ALL snow maps (supersedes v6)

Benjamin, on v6: "Add double transitional colors on top of that too, adjusted the numbers if needed."

- **Source of truth:** `snow_scale.py` / `snow_scale.json`. Use `build("change")` for depth-change maps and `build("amount")` for snow depth and snowfall totals: gain half only, < 0.1 in = no fill, 60+ = white. `style_draft.build_snow_chg(slug, ver="v7")` mirrors it. v6 is frozen in `snow_scale_v6.py` / `snow_scale_v6.json`.
- **56 colors** (v6: 28): under (< -24) + 16 loss bins, no fill (-1 to +0.1 in), 37 gain bins, white 60+.
  - **Gain edges:** 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4 … 12 by 1, 13.5 … 24 by 1.5, 27 … 60 by 3.
  - **Loss edges:** -24, -21, -18, -15, -12, -10, -8, -7, -6, -5, -4, -3.5, -3, -2.5, -2, -1.5, -1.
- **Same hue path as v4–v6.** Each v7 bin takes the v6 color at its position on the v6 scale (CIELAB interpolation), so any value keeps about the same color. There is a paler blue at the very bottom, and the indigo dip (12–16.5 in) is hand-smoothed for color-blind separation.
- **Key:** every bin is a swatch, but only `snow_scale.KEY_TICKS` are labeled (-24, -18, -12, -8, -6, -4, -3, -2, -1, 0.1, 0.5, 1, 2, 3, 6, 8, 10, 12, 15, 18, 21, 24, 30, 36, 42, 48, 54, 60). The -1 and 0.1 labels are pushed apart around the one-swatch no-fill bin. The white 60+ triangle is about 1.4 swatches wide.
- **White top bin:** dark outline `#06101A` on chips and keys, thin dark contour at 60 in on maps.
- **CVD check (relaxed flag for fine neighbours):** adjacent bins ≥ 2.3 dE (CIE76 ≈ one just-noticeable difference) and bins two apart ≥ 5 dE (the normal flag) in every vision type. Result: adjacent min 3.4 normal, 2.6 deutan, 3.2 protan, 2.8 tritan; two-apart min 8.6, 6.9, 6.7, 6.0. Pass. Gain vs land `#1E2B37` ≥ 13.5.
- **Known look:** the 12–16.5 in indigo is the darkest step (lightness dips, then rises to white), so maps show a dark indigo ring between the blues and purples. This is inherited from v6.

| Bin (in) | Color |
|---|---|
| < -24 | `#5E1A20` |
| -24 to -21 | `#702124` |
| -21 to -18 | `#7C2726` |
| -18 to -15 | `#882C29` |
| -15 to -12 | `#94332B` |
| -12 to -10 | `#A23C2C` |
| -10 to -8 | `#B2472D` |
| -8 to -7 | `#BF4F2D` |
| -7 to -6 | `#C4572F` |
| -6 to -5 | `#CC6431` |
| -5 to -4 | `#D57435` |
| -4 to -3.5 | `#DC8038` |
| -3.5 to -3 | `#E18D47` |
| -3 to -2.5 | `#E79E5A` |
| -2.5 to -2 | `#EDB270` |
| -2 to -1.5 | `#F1C587` |
| -1.5 to -1 | `#F3CF92` |
| -1 to 0.1 (no fill) | no fill |
| 0.1-0.25 | `#D4EBFA` |
| 0.25-0.5 | `#C8E5F8` |
| 0.5-0.75 | `#B8DBF5` |
| 0.75-1 | `#AAD3F1` |
| 1-1.5 | `#9BCAEE` |
| 1.5-2 | `#8DC1EA` |
| 2-2.5 | `#80B6E5` |
| 2.5-3 | `#72ACE1` |
| 3-4 | `#619FDB` |
| 4-5 | `#5490D3` |
| 5-6 | `#4980CB` |
| 6-7 | `#4074C4` |
| 7-8 | `#3A6CC0` |
| 8-9 | `#3661B7` |
| 9-10 | `#3255AF` |
| 10-11 | `#2E4AA6` |
| 11-12 | `#2A3D98` |
| 12-13.5 | `#26358C` |
| 13.5-15 | `#26267F` |
| 15-16.5 | `#352491` |
| 16.5-18 | `#472DA2` |
| 18-19.5 | `#5833AE` |
| 19.5-21 | `#6939B7` |
| 21-22.5 | `#7B40BE` |
| 22.5-24 | `#8D47C5` |
| 24-27 | `#9E4ECC` |
| 27-30 | `#AC55D0` |
| 30-33 | `#B75CCF` |
| 33-36 | `#C263CE` |
| 36-39 | `#CD6ACD` |
| 39-42 | `#D674CD` |
| 42-45 | `#DD7FD0` |
| 45-48 | `#E48AD2` |
| 48-51 | `#EB95D5` |
| 51-54 | `#F1A5DA` |
| 54-57 | `#F6BBE2` |
| 57-60 | `#FAD4EC` |
| 60+ | `#FFFFFF` (dark outline `#06101A`) |


## Added 2026-11-03 4:25 PM PST: Wind barbs and line weights (Benjamin 11-03-26 ~4:14 PM PST: "knots symbols that accurately reflect the wind speed… make map lines thicker")
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

Source: `render_gfs_products_light_v2.py` (`LINE_W`, `BARB`, `draw_barbs`).
