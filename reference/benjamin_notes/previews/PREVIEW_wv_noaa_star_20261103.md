# Preview + QA: water vapor from NOAA/NESDIS/STAR (IEM removed) + satellite credit fixes (11-03-26)
Requests: t2233u (only 100%-clear satellite sources), t2238u ("Use whatever the best NOAA mid level one is that we can use"),
t2239u (no meaningful storage writes / runtime / Actions; no collector or render job). Standing go-ahead t2209u/t2225u.
Branch wv-star (worktree wx-models-site/wv2) off origin/main bb83b14 (prod ec3b97d2).
Hidden previews: c14d72c1, d9549792, d64ff676, ea3f3297, 012ff76f, c968dcfa (pv1 full QA PASS), d5fa85dd, 939797e1 (pv3), ec65e1f8 (pv4, final, after the view-switch fix). Production ece4989f (c13c953), QA in radar_goes_qa/wv2/prod2; first deploy 2a60cc7e failed prod QA (CORS/404 on view switch) and was rolled back.

## Source (water vapor = GOES-18 ABI band 9, 6.9 um, mid-level)
- NOAA/NESDIS/STAR CDN, browser-direct (CORS *): https://cdn.star.nesdis.noaa.gov/GOES18/ABI/SECTOR/pnw/09/ (1200 px, every 5 min),
  .../SECTOR/wus/09/ (1000 px = 2 km, every 10 min), .../FD/09/ (full disk 1808 px = 6 km, every 10 min). Layered full disk < West US < PNW.
- Terms (CLEAR): STAR "Users are free to use the images or information hosted on this site as they wish, as long as credit is given to the
  NOAA / NESDIS Center for Satellite Applications and Research." Credit shown: "Satellite: NOAA GOES-West Mid-Level Water Vapor (band 9), NOAA/NESDIS/STAR".
- Geometry: the JPGs are crops of the GOES-18 ABI fixed grid (sub-point 137.0 W). Crop offsets / pixel size fitted to NOAA's own burned-in red
  map lines: pnw x0 0.0217291 y0 0.1271681 rad, 28.0 urad px; wus x0 -0.0031458 y0 0.1367099, 56.0 urad; full disk = nominal grid (+/-0.151872, 168 urad).
  99% of NOAA state/border line points land within 1 px (random pixels 5%); same on 10-day-old frames. Reprojected per pixel in WebGL under our map.
- Clean-up in the browser: red map-line pixels masked (+2 px, +3 px on the full disk) and filled from surrounding pixels; NOAA logo and time bar cut.
  Every frame is re-checked against 300 reference line pixels; if NOAA ever moves a sector the frame is skipped and the layer says so.
- Loop: the CDN lists ~10 days of frames, so a full 12-frame loop (1 h on PNW / Puget Sound, 2 h on the wide view) loads on first open:
  first frame ~0.7 s, all 12 ~3 s in QA. Latency ~5-10 min. No collector, no R2, no Actions, nothing stored by us (old IEM IndexedDB store deleted).
- Removed: all Iowa Environmental Mesonet satellite code (WMS, JSON, IndexedDB frame store, "loop builds while open") and the IEM WV credit.
  (IEM station dots on the Observations map unchanged, out of scope.)

## Credits
- Page (Observations credits, viewer + Studio panel): new paragraph incl. the exact GIBS sentence "We acknowledge the use of imagery provided by
  services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS)."
- GeoColor: "Satellite: NOAA GOES-West GeoColor, NOAA/NESDIS/STAR, CIRA/NOAA via NASA GIBS/ESDIS".
- Downloads (obs.js credit strip now wraps to extra lines) and Studio PNG/MP4 credit lines add the GIBS sentence when Clean IR or GeoColor is on.
