# Satellite terms, final check (Observations map), 11-3-26 ~8:20 PM PST
Read-only. No code changed, nothing deployed. Terms pages re-fetched today. Credits checked in the latest code, satzoom/web/forecast/obs/obsimg.js.

## Verdicts
| Source | Verdict | Credit required | Shown on site? |
|---|---|---|---|
| Radar: NCEP opengeo MRMS conus_bref_qcd | CLEAR (NWS public domain) | None required; don't claim it as your own, imply NWS endorsement, or present edited data as official | Yes: layer and download credit "Radar: NOAA/NWS MRMS base reflectivity (public domain)"; page credits say "NOAA/NWS NCEP MRMS" |
| Clean IR band 13 via NASA GIBS | CLEAR (NASA open data, CC0 unless marked; GOES is NOAA/US gov) | GIBS asks for its acknowledgment sentence | Yes: layer credit plus the full GIBS sentence on the page, in downloads and in Studio |
| GeoColor via NASA GIBS (made by NOAA/NESDIS/STAR, CIRA/RAMMB) | CLEAR (STAR: free to use "as they wish" with credit; CIRA asks only for "credit CIRA/NOAA"; no redistribution or commercial limit found) | GIBS sentence, NOAA/NESDIS/STAR, CIRA/NOAA | Yes: "NOAA/NESDIS/STAR, CIRA/NOAA via NASA GIBS/ESDIS" plus the GIBS sentence |
| Water vapor band 9, STAR CDN | CLEAR (same STAR terms) | Credit NOAA/NESDIS Center for Satellite Applications and Research | Yes: "..., NOAA/NESDIS/STAR" |

No credit fix needed. The earlier gap (STAR missing from the GeoColor credit) is fixed in the live code.

Remaining caveats (none of them limit use):
- STAR says its images are "not official NOAA operational products" and may be interrupted without notice. This is about reliability, not a use restriction.
- The water vapor images are edited in the browser (burned-in lines and logo removed). That's fine as long as the site doesn't present them as official NOAA products, and it doesn't.
- GeoColor's night city lights are a static NOAA JPSS VIIRS layer (government data).
- Optional wording polish: "NOAA/NESDIS/STAR" could be spelled out once on the page as "NOAA/NESDIS Center for Satellite Applications and Research", matching the exact wording STAR asks for. The abbreviation already credits STAR.
- Base layers: Natural Earth (public domain), and GeoNames (CC BY 4.0, credited). Unchanged.

## Key quotes (fetched 11-3-26)
- https://www.star.nesdis.noaa.gov/star/productdisclaimer.php : "Users are free to use the images or information hosted on this site as they wish, as long as credit is given to the NOAA / NESDIS Center for Satellite Applications and Research."
- https://www.star.nesdis.noaa.gov/GOES/fulldisk_band.php?band=GEOCOLOR&sat=G18 : "GeoColor was developed at the Cooperative Institute for Research in the Atmosphere (CIRA) and the STAR Regional and Mesoscale Meteorology Branch (RAMMB). ... Please credit CIRA/NOAA when using GeoColor imagery."
- https://nasa-gibs.github.io/gibs-api-docs/ : "NASA promotes full and open sharing of data. We ask that users who make use of GIBS in their clients ... add the following acknowledgment: We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS)."
- https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance (quoted in SATELLITE_TERMS.md from the earlier fetch today, not re-fetched this pass): "data provided from a NASA-led mission are licensed as Creative Commons Zero (CC0). While there are no restrictions on the use of these data..."
- https://www.weather.gov/disclaimer : "The information on National Weather Service (NWS) Web pages are in the public domain, unless specifically noted otherwise, and may be used without charge for any lawful purpose so long as you do not: 1) claim it is your own ..., 2) use it in a manner that implies an endorsement or affiliation with NOAA/NWS, or 3) modify its content and then present it as official government material."
