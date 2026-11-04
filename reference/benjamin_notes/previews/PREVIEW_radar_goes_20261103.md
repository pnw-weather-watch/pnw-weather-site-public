# Radar + GOES-West satellite layers on the Observations map - 11-03-26 PST
Approved: Benjamin t2209u 11:43 AM "Go ahead and do it all, push and deploy as you check each one off the list".
Hidden previews: 2064ad06 (first), 8a0fda32, 609f7354 (Studio PNG/MP4 QA), 8856a612, 9f8c0a2a (final). Production: 3a382136 (9555dc5), previous 54f5e4d7.
Commits on main (fast-forward 06aa1d8..9555dc5): 18f05ca, 18f4f74, 368a340, 070dadb, 9555dc5.
What: Observations map (viewer Observations window and Studio > Observations) gets a second chip row: Radar | Satellite: Clean IR | Satellite: GeoColor,
all OFF by default (not remembered between visits). Radar + one satellite can be on together (satellite under radar). Loop of 12 frames
(radar ~1 h at ~5-6 min steps, satellite 2 h at 10 min), pause/play + frame slider, frame times in PT next to the slider.
Imagery is reprojected per pixel (WebGL) into the obs map's own Lambert projection, so zoom / pan / pinch / view buttons move it with the map;
drawn over the land fill, under coastlines, borders, isobars and station plots. Two boxes per source (detail PNW when zoomed in, wide for the West view).
Studio: credits added to the frame credit lines, legend pills "Radar 2:24 PM PT" / "Satellite Clean IR 1:40 PM PT", title "Radar" / "GOES-West Satellite" /
"Radar and Satellite" when no station layer is on; MP4 export steps the loop across the video (first frame -> newest); PNG carries the shown frame.
Viewer "Download image" credit strip adds the radar / satellite credits.
Sources (browser-direct, CORS "*", no keys, no server, nothing stored by us):
 - Radar: NOAA/NWS NCEP MRMS QC'd 1 km base reflectivity mosaic, WMS opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd (US government work, public domain).
   Credit shown: "Radar: NOAA/NWS MRMS base reflectivity (public domain)". CONUS mosaic only (no Canadian radars; echoes stop ~at the border).
 - Satellite: NOAA GOES-West (GOES-18) ABI via NASA GIBS WMS (epsg4326 best): GOES-West_ABI_Band13_Clean_Infrared, GOES-West_ABI_GeoColor.
   NASA: no use restrictions; requested acknowledgment "imagery provided by services from NASA's GIBS, part of NASA's ESDIS"; GeoColor: "please credit CIRA/NOAA".
   Credits shown: "Satellite: NOAA GOES-West Clean IR (band 13) via NASA GIBS/ESDIS" / "Satellite: NOAA GOES-West GeoColor (CIRA/NOAA) via NASA GIBS/ESDIS".
Limits: satellite is ~35-60 min behind real time (GIBS latency; newest listed frames that are still black are dropped and retried). Faster sources were rejected:
 NESDIS STAR CDN sector JPGs have burned-in borders/logo/caption; nowCOAST GOES is band 14 (not Clean IR), stops at 50.5N, has an E/W seam.
 Needs WebGL (message shown if off). Wide boxes end at 72N / 94W (edge visible far out in the West view). Phone: 2 layers x 12 frames ~ 20-40 MB of images in memory.
Storage / runtime added: none (0 R2 objects, no workflow, no cron). Per viewer session with a layer on: radar ~12 x 0.1-0.3 MB, satellite ~12 x 0.3-0.6 MB.
Radar tab / Studio GOES-West window: neither exists in the site code (searched viewer, studio, index, old-site web/forecast, all worktrees), so nothing was removed or redirected.
QA (preview + production; Chromium desk 1512x945@2x + phone 390x844@3x): 0 console/page errors, 0 bad responses; toggles off by default; loop advances;
pause holds; zoom +/drag keeps imagery registered with coastlines; West view uses wide boxes; canvas export not tainted; all off -> 0 images kept;
smoke viewer/compare/social/wamaps/meteograms/studio 0 errors (data proxy /d/ OK). Studio: PNG 1080x1920 saved, MP4 1080x1920 H.264 150 frames,
loop steps (frame 0 GeoColor 11:50 AM / radar 1:21 PM -> frame 140 1:40 PM / 2:28 PM).
Screens: /workspace/radar_goes_qa/pv5/ (final preview), pv3/ (Studio PNG/MP4 + frames mp4_strip.jpg), prod/ (production).
Production Studio QA PASS 11-03-26 2:57 PM PST: PNG + MP4 (150 fr, loop advances), 0 errors; strip prod/mp4_strip.jpg.
