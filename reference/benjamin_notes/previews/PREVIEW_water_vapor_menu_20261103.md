# Preview + QA: Observations water vapor satellite, Hide menu, phone scrolling (11-03-26)
Requests: t2224u/t2225u (clean IR + mid-level water vapor, push + deploy once built), t2226u (minimize menu, phone scroll, Studio?).
Hidden previews: b20bf88e (f4c77ae), b0f36197 (rebased bb83b14). Production: ec3b97d2 (bb83b14). Rollback: ROLLBACK_prod_ec3b97d2_20261103.md.
## Source decision (water vapor = GOES-West ABI band 9, 6.9 um)
- NASA GIBS has no band 9 layer (GOES-West: Band13 Clean IR, Band2 Red Visible, GeoColor, Air Mass, Dust, FireTemp only).
- Rejected: nowCOAST (band 8, East+West mosaic, north edge 50.55N), CIRA SLIDER (no CORS), AWS noaa-goes18 (14 MB netCDF, no CORS),
  RealEarth (watermarks unregistered sites; needs an account), Unidata THREDDS (netCDF only).
- Used: Iowa Environmental Mesonet GOES-West WMS https://mesonet.agron.iastate.edu/cgi-bin/wms/goes_west.cgi (CORS *, AccessConstraints None,
  NOAA GOES-18 data, public domain). PNW box: conus_ch09 (2 km, 5-min) over fulldisk_ch09 (6 km, 10-min; fills north of ~50-53N, visibly
  coarser there). Wide box: fulldisk_ch09. IEM colour WV table (yellow = dry, blue = moist, white = very moist / cold cloud).
- Latency measured: newest image about 4-10 min behind real time (much fresher than GIBS Clean IR/GeoColor at 40-60 min).
- Limit: IEM serves only the newest image, so the loop is built in the browser (IndexedDB, last 3 h, up to 24 frames per box, loop shows 12):
  first open shows one frame ("water vapor loop builds while open"), +1 frame every 5 min (PNW) / 10 min (wide) while it is on; kept across reloads
  on that device. A full instant 1-2 h loop would need a small server-side collector (R2 ~26k writes/month) - not built.
- Credit: "Satellite: NOAA GOES-West Mid-Level Water Vapor (band 9) via Iowa Environmental Mesonet" (on downloads, Studio PNG/MP4 credit strip).
## UI
- Satellite chips now read "Satellite: [Clean IR] [GeoColor] [Water vapor]" (mutually exclusive; Radar overlays any). Clean IR (band 13) unchanged.
- Studio legend pills: "Satellite Clean IR (band 13)", "Satellite GeoColor", "Satellite Mid-Level Water Vapor (band 9)".
- "Hide menu / Show menu" button: viewer = Observations title bar; Studio = top of the Observations panel. Hides view + layer + satellite chips,
  keeps the loop play/slider; remembered (localStorage obsMenuMin). Viewer map grows when minimized. Exports unaffected (Studio frames are drawn from map state).
- Viewer Observations window now scrolls (phone could not reach Download/Refresh/notes/credits); 72 px bottom padding clears the pencil button.
- Studio phone page already scrolled; verified panel + both frames reachable, minimized and expanded.
## QA (0 page errors, 0 console errors, 0 failed requests in every run)
- Screenshots: /workspace/radar_goes_qa/wv/pv1 (preview, viewer + Studio desk/phone), wv/pv2 (rebased, viewer), wv/prod (production, all).
- Studio exports: PNG 1080x1920 + MP4 1080x1920 H.264 150 frames with Radar + Water vapor (wv/pv1, wv/prod).
