# Credits and legal record

Verified Tue Nov 3, 2026, 12:45 PM PST, from the source pages linked below. This is a reading of each provider's published terms, not legal advice. Rules are in `LEGAL_RULES.md`.

## On-image credit (the only one required)

ECMWF open data is CC BY 4.0 **plus** the ECMWF Terms of Use. The Terms of Use say attribution "must be displayed prominently" and must include "…based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF)". The required wording for a data product is: © [year] ECMWF; source www.ecmwf.int; the CC BY 4.0 licence statement and link; the disclaimer; and an indication of modification. Our maps are modified (we compute snow depth change, convert units and regrid for display). Each standalone image therefore carries, in two footer lines:

> Based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF), modified (snow depth change computed) · © 2026 ECMWF · ecmwf.int · CC BY 4.0 creativecommons.org/licenses/by/4.0
> ECMWF does not accept any liability whatsoever for any error or omission in the data, their availability, or for any loss or damage arising from their use.

- The short form "Data: ECMWF, CC BY 4.0 (modified)" used in v1-v4 is **not enough on its own**. It lacks the "based on data and products of ECMWF" wording and the disclaimer that the ECMWF Terms of Use require.
- **Possible one-line version, once the site has a public credits URL:** CC BY 4.0 §3(a)(1) allows credit "in any reasonable manner… by providing a URI… to a resource that includes the required information". The line could then read "Based on data and products of ECMWF (modified) · © 2026 ECMWF · CC BY 4.0 · Disclaimer and credits: <site>/credits". That version moves the disclaimer to the credits page. ECMWF's terms list the disclaimer as wording to be "attached to the use", so the two-line form stays the default for images posted on social media without a link.
- Maps made only from NOAA/USGS/Census/Natural Earth data need **no** on-image credit.

## Site About / Credits page (full wording for the service)

The ECMWF Terms of Use set a separate wording for **services** built on the data. Put this on the site's About/Credits page, linked from every page footer:

> This service is based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF). Source: www.ecmwf.int. This ECMWF data is published under a Creative Commons Attribution 4.0 International (CC BY 4.0) licence, https://creativecommons.org/licenses/by/4.0/. ECMWF does not accept any liability whatsoever for any error or omission in the data, their availability, or for any loss or damage arising from their use. The ECMWF data shown here has been modified (derived fields, unit conversion, interpolation and display binning).

Also list the courtesy credits below. None of them are required, but they are good practice and keep the Census Bureau's citation request.

## Source and asset register

| Element (v5 pass view) | Source / asset | License | Commercial use | On-image credit | Terms verified at (2026-11-03) |
|---|---|---|---|---|---|
| Snow depth change field (sd, rsn, z) | ECMWF IFS 0.25° open data, data.ecmwf.int (free, no login) | CC BY 4.0 + ECMWF Terms of Use | Yes ("may be redistributed and used commercially, subject to appropriate attribution") | **Required** (above) | https://www.ecmwf.int/en/forecasts/datasets/open-data ; https://apps.ecmwf.int/datasets/licences/general/ ; https://creativecommons.org/licenses/by/4.0/legalcode.en |
| Roads | US Census Bureau TIGER/Line 2024 primary + secondary roads (CA, NV) | US Gov work, no copyright (17 U.S.C. §105) | Yes | None (Census "asks" for a citation; given on credits page). Never use "TIGER/Line" in a product name | https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2024/TGRSHP2024_TechDoc_Ch1.pdf |
| Pass points and elevations | USGS GNIS | USGS public domain | Yes | None (USGS requests credit; given on credits page) | https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits |
| Coast, lakes, state lines, land/ocean, Nevada outline in the NV shield | Natural Earth 10m | Public domain | Yes ("No permission is needed… Crediting the authors is unnecessary") | None | https://www.naturalearthdata.com/about/terms-of-use/ |
| Interstate shields I-5, I-80 | Wikimedia Commons SVGs (assets/shields/*.license.json: PD-MUTCD / PD-USGov-MUTCD, restriction "trademarked") | Public domain artwork; **shield design is a registered AASHTO trademark (Reg. 835,635)** | Yes for truthful identification of the actual Interstate on a map (nominative use; MUTCD names it as the one trademark exception) | None | https://commons.wikimedia.org/wiki/Template:PD-MUTCD ; https://commons.wikimedia.org/wiki/Commons:WikiProject_U.S._Roads/Licensing ; https://www.fhwa.dot.gov/interstate/faq.cfm |
| US route shields US 50, US 395 | Wikimedia Commons SVGs (PD-USGov-MUTCD, no restrictions) | Public domain | Yes | None | same as above |
| CA state route shields (spade), NV state route shields, green summit sign cards | Original drawings in `shields_v3.py` / render scripts (no copied artwork) | Ours | Yes | None | n/a (own work; NV outline from Natural Earth PD) |
| Fonts: Space Grotesk, IBM Plex Sans, IBM Plex Sans Condensed, Overpass 700/800 | Font files in `fonts/` (OFL.txt in each folder; Overpass OFL copied in from the Overpass project license 2026-11-03) | SIL Open Font License 1.1 | Yes (embedding in images is allowed; only selling the font files on their own is barred) | None required | https://openfontlicense.org (license text in each fonts/*/OFL.txt; font name-table license fields checked) |
| Color scales, layout | Original (style_draft.py, snow_scale.py / snow_scale.json, snow_scale_v6.*) | Ours | Yes | None | n/a |
| Removed in v4: hillshade relief | USGS 3DEP (public domain) | — | — | Credit removed with the layer | — |
| Pass sampling only (not drawn), NBM NorCal pass views v2 / snow v1 | USGS 3DEP elevation, The National Map 3DEPElevation ImageServer exportImage (`data/fetch_3dep_norcal_v1.py`, public, no login) | Public domain; "free of charge and without use restrictions" | Yes | None on image (USGS *requests* "Data available from U.S. Geological Survey, National Geospatial Program." when citing; give it on the credits page) | Checked Tue Nov 3, 2026 (PST): https://www.usgs.gov/3d-elevation-program/about-3dep-products-services and https://www.usgs.gov/faqs/what-are-terms-uselicensing-map-services-and-data-national-map |

Other sources already approved for the site (same rules; re-check each before first use): NOAA GFS / GEFS / NBM / RRFS / GFS-Wave (NOAA/NWS public domain; don't imply NOAA endorsement; don't present modified data as official), https://www.weather.gov/disclaimer. NOAA OISST from NCEI (public domain; NCEI asks for a citation, which goes on the credits page). ECMWF AIFS open data (same CC BY 4.0 + Terms of Use as IFS).

## NBM PNW temperature mock (v1, added Tue Nov 3, 2026, 1:00 PM PST)

| Element | Source / asset | License | Commercial use | On-image credit | Terms verified at (2026-11-03) |
|---|---|---|---|---|---|
| Daytime high (TMAX 2 m, 12-hr max) | NOAA National Blend of Models (NBM) CONUS 2.5 km core GRIB2, AWS Open Data bucket noaa-nbm-grib2-pds (no account, byte-range download via the .idx) | NOAA/NWS US Gov work, public domain; NODD terms: "open to the public and can be used as desired" | Yes | None required. NOAA *requests* attribution only for unaltered data (ours is modified: unit conversion, interpolation, binning), so credit goes on the credits page. Must not state or imply NOAA endorsement/affiliation, and must not present modified data as original unaltered NOAA data | https://registry.opendata.aws/noaa-nbm/ ; https://www.weather.gov/disclaimer |
| PNW airport (ASOS) station locations | NWS API station metadata, api.weather.gov/stations/{ICAO} (`pnw_airports.csv`, also used for `ca_airports.csv`) | NOAA/NWS US Gov work, public domain | Yes | None | https://www.weather.gov/disclaimer ; https://www.weather.gov/documentation/services-web-api |
| Basemap lines, fonts, color scale | same Natural Earth / OFL fonts / own t2m scale as above | as above | Yes | None | as above |

## RRFS PNW wind-gust mock (F075, v1, added Tue Nov 3, 2026, 1:15 PM PST) - new source for the site

| Element | Source / asset | License | Commercial use | On-image credit | Terms verified at (2026-11-03) |
|---|---|---|---|---|---|
| Wind gust (GUST, surface level = the model's 10 m-type surface gust) | NOAA Rapid Refresh Forecast System (RRFS v1, operational since Oct 14, 2026), CONUS 3 km Lambert 2dfld GRIB2, AWS Open Data bucket noaa-rrfs-ops-pds (no account; byte-range via .idx). Same files on NOMADS. The old prototype bucket noaa-rrfs-pds (rrfs_a/) is no longer updated | NOAA NODD: **CC0-1.0 public domain dedication**, "no restrictions on the use of the data" | Yes | None required. NOAA requests attribution for unaltered data only (ours is modified: unit conversion, interpolation, binning), so it goes on the credits page. Must not state or imply NOAA endorsement/affiliation, and must not present modified data as original unaltered NOAA data. Suggested citation for the credits page: "NOAA Rapid Refresh Forecast System (RRFS) and RRFS Ensemble Forecast System (REFS) [Operational] was accessed on DATE from https://registry.opendata.aws/noaa-rrfs-ops" | https://registry.opendata.aws/noaa-rrfs-ops/ ; https://www.nco.ncep.noaa.gov/pmb/products/rrfs/ ; https://www.weather.gov/disclaimer |

Note: the NODD license wording now says CC0-1.0 for all NOAA NODD datasets (this also covers NBM, GFS, GFS-Wave on AWS).

## Not cleanly commercial-safe (open items)
- **Interstate shield (trademark, not copyright).** Fine for marking the real I-5 / I-80 on a map; this is standard practice on commercial maps. Don't use it in logos, thumbnails or branding, or for non-Interstate routes. If Benjamin wants zero trademark exposure, swap it for an original blue/red "I-80" badge in `shields_v3.py` (about 15 min of work).
- No other element has NC, SA or unclear terms.

## Product-looks mocks v1 (added Tue Nov 3, 2026, 3:40 PM PST) - anomaly climatology, PENDING Benjamin's OK

| Element | Source / asset | License | Commercial use | On-image credit | Terms verified at (2026-11-03) |
|---|---|---|---|---|---|
| 300 mb u/v/height, 500 mb height, 850 mb temp, surface pressure (below-ground mask) | NOAA GFS 0.25° pgrb2, AWS Open Data noaa-gfs-bdp-pds (byte-range via .idx, `data/fetch_gfs_products_v1.py`) | NOAA NODD CC0-1.0 / US Gov public domain | Yes | None | https://registry.opendata.aws/noaa-gfs-bdp-pds/ ; https://www.weather.gov/disclaimer |
| Anomaly baseline (500 mb height, 850 mb temp) | NCEP/NCAR Reanalysis 1 monthly long-term means 1991-2020, NOAA PSL, downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/pressure/{hgt,air}.mon.ltm.1991-2020.nc (no login) | PSL: "information on federal government servers are in the public domain ... may be used freely by the public" (no claiming it as ours, no implied NOAA endorsement, no presenting modified data as official) | Yes | None required. PSL *asks* for: "Data provided by the NOAA PSL, Boulder, Colorado, USA, from their website at https://psl.noaa.gov" plus the dataset citation Kalnay et al. 1996, BAMS 77, 437-471 -> credits page | https://psl.noaa.gov/data/help/ ; https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.derived.html ; https://psl.noaa.gov/data/atmoswrit/reference.html |

Note: the reanalysis is a joint NCEP/NCAR product; PSL distributes it from a federal server under the public-domain statement above. Same source the old site's `make_clim*.py` use. Status: used in design mocks only; needs Benjamin's OK as a site source (LEGAL_RULES rule 7 / starter prompt rule 5).
Also used (v2 mocks, 4:05 PM PST): GFS PRMSL and 10 m u/v from the same GFS file (already covered by the row above). Color scales are our own original "Aurora Reef" palettes (no third-party color tables), so there's nothing to credit.
Not used: ERA5 climatology (Copernicus CDS). Licence is CC BY 4.0 since 2 July 2025 (commercial OK with attribution), but downloads need a registered CDS account (CDS Terms of Use, Art. 2), which breaks LEGAL_RULES rule 1 (no sign-in), and it would add another required on-image credit (rule 5). https://cds.climate.copernicus.eu/licences/cc-by ; https://cds.climate.copernicus.eu/licences/terms-of-use-cds


## No third-party palettes copied (Tue Nov 3, 2026)
- No color tables, palettes, images, code, logos or branding from WeatherBell, Pivotal, Tropical Tidbits, weathermodels.com or any other site are used.
  - Every scale, including the reference-look v1 and v2 anomaly scales, is built from our own anchor colors in our own scripts.
- Other sites' colors were looked at **only for comparison**, to stay distinct (see `WEATHERBELL_COMPARISON_v1.md`). Nothing was saved from WeatherBell.
- The reference colorbar row in the strip images is sampled from Benjamin's own attachment. It's used only in internal comparison strips, never on published maps.
- A generic diverging look (blue below, red above, white near normal) is a common scientific convention, not anyone's property.
- **Canonical anomaly scale `anom_scale.py` / `anom_scale.json` (v4, Tue Nov 3, 2026):** an original palette.
  - It's our own v3 anchors smoothed in OKLab. It isn't copied from WeatherBell or any other site, and it needs no credit on images.

## ECMWF wave fields (added Tue Nov 3, 2026 ~9:45 PM PST)
- **Source:** ECMWF IFS HRES-WAM 0.25° open data, stream=wave (swh, mwd, pp1d, mwp) from data.ecmwf.int. Free, no login.
- **Terms:** CC BY 4.0 plus the ECMWF Terms of Use, the same as the IFS row above. Benjamin approved ECMWF open data for this site.
- **Credit on every wave image:** the full two-line credit above (the "Based on data and products of ECMWF, modified …" line plus the disclaimer).
  - The modifications are: unit conversion m → ft, the derived max wave (1.86 × swh), smoothing and display binning.
- **No max-wave field:** the open set has no maximum individual wave height field (hmax). The "Estimated maximum wave height" is derived as 1.86 × swh, and the image says so.
- **Buoys:** NDBC buoy values are NOT used. They would be a new source (NOAA, public domain) and need approval first.

## Sources added Wed Nov 4, 2026 (second site)
- **NOAA NWS NWPS, Nearshore Wave Prediction System (Honolulu office), via NOMADS `prnwps`:** US Government work, public domain. No credit is legally required. Optional courtesy line: "Nearshore waves: NOAA/NWS NWPS".
  - Used for the Hawaii coast-town wave numbers on the Waves tab, Hawaii (wide) view.
  - Grids: CG2 Kauai, CG3 Oahu and CG4 Maui at about 500 m; CG1 for all islands at about 2.7 km (the only one covering the Big Island).
  - Towns-offshore table: `nearshore/hfo.json` → `towns` (grid, lat/lon, distance from the town pin, at least 400 m). Built by `tools/fast/nearshore_hfo.py`.
  - Finest legal resolution found: about 500 m. No free source gives a true 1/4 mile (400 m) grid. Town numbers are the model cell about 0.25–0.45 mi offshore (Kauai, Oahu, Maui) or a 2.7 km cell about 0.5–0.7 mi offshore (Big Island).
- **PacIOOS SWAN (Univ. of Hawaii), 500 m:** NOT used. Its terms say the data "may be used and redistributed for free but is not intended for legal use" and ask for acknowledgment. Commercial or monetized use isn't explicitly addressed, so Benjamin has to approve it first.
- **NOAA PSL NCEP/NCAR Reanalysis 1, SLP monthly long-term mean 1991–2020 (`slp.mon.ltm.1991-2020.nc`):** US Government, public domain. Used for the MSLP anomaly normals (`tools/fast/clim/ncep_slp_mon_ltm_1991_2020.npz`).
  - Courtesy line, already in the run line: "vs 1991–2020 NCEP/NCAR monthly normal". No image credit is legally required.
- **Natural Earth 10m roads (`ne_10m_roads`):** public domain. Used for the major interstate and US highway lines on the Sierra Passes view. Covered by the existing "Basemap: Natural Earth" credit.
- **Pass elevations, California:** regions.json `CA_PASSES` `elev_ft` (facts, no license needed).
