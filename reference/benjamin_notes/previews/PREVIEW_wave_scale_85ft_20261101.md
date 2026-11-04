# SHIPPED 11-01-2026 ~10:07 AM PST: OFFSHORE MARKERS (edbbec9) + LABEL MOVES (f1e96cc) -> production 20c07c0d = origin/main f1e96cc (prev 89da4f96).
  See ROLLBACK_prod_20c07c0d_20261101.md. Branch label_moves (preview 31dcf462): Neah Bay -> Tatoosh Island (48.392,-124.736; marker 48.392,-124.75),
  Bellingham -> Birch Bay (48.918,-122.765; marker 48.91,-122.79), Victoria + Olympia off, Everett 47.985,-122.255 (Possession Sound), Port Townsend
  48.135,-122.72 (Admiralty Inlet, number read there), Seattle 47.605,-122.36 (Elliott Bay), Tacoma 47.295,-122.475 (west Commencement Bay); waves +
  wavemax + wavemax24, all views. Preview QA local + 31dcf462 0 errors (lbl_*.png); prod QA qa_prod_lbl.py 0 errors (prod_*_lbl.png).

# UPDATE 11-01-2026 ~10:00 AM PST: coast town numbers from a 0.5 mi OFFSHORE marker (Benjamin t2004u), HIDDEN PREVIEW ONLY, NOT approved to ship
- Branch offshore_samples, commit edbbec9 on main b3a9e4f (viewer.js?v=20261101q). NOT pushed. Production still 89da4f96.
- Preview 14b73056: https://14b73056.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=wavemax&view=wa
- viewer.js offshorePt(): OFFSHORE explicit points (Neah Bay, La Push, Ocean Shores, Westport, Long Beach, Cannon Beach, Port Angeles, Victoria,
  Bellingham, Smith Island, Port Townsend, Shore Acres, Coos Bay, Eureka, San Francisco, San Diego, Monterey, Santa Barbara, Los Angeles, Crescent City),
  else OFF_BRG bearing + 0.8 km, default due west. offVal(): seaVal at the marker (bilinear if 4 sea points, else nearest sea point within 1.5 cells
  of the marker); none -> town point (logged). Buoys unchanged; Seattle/Everett/Tacoma/Olympia still names only.
- F+300 wavemax WA before -> after: Westport 4 -> 22, Neah Bay 18 -> 14, Long Beach 18 -> 19, Bellingham 1 -> 3; all others unchanged (0.25 deg grid).
- QA qa_off.py 0 console errors; off_*.png. To ship (only on "Push"/"Deploy"): git checkout main && git merge --ff-only offshore_samples && push;
  deploy --branch=main. Undo: git branch -D offshore_samples.

# SHIPPED 11-01-2026 ~9:48 AM PST: WAVE LABELS + WEST COAST VIEW -> production 89da4f96 = origin/main b3a9e4f (prev 10e0714e). See ROLLBACK_prod_89da4f96_20261101.md.
  QA qa_prod_wc.py 0 console errors (WA waves/wavemax/wavemax24, PNW, PNW tight, Puget, wc x3, t2m on wc -> pnw fallback, t2m wa, Studio wa + wc); prod_*_wcship*.png.

# UPDATE 11-01-2026 ~9:50 AM PST: WAVE MAP LABELS (t1998u, t2001u) + WEST COAST view (t1999u, t2000u), HIDDEN PREVIEW ONLY, NOT approved to ship
- Branch wa_wave_labels: d2e319d on main db0b104 (viewer.js?v=20261101o). Preview dc0df2f0: https://dc0df2f0.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=waves&view=wa
  Wave views with a town layer no longer draw the static towns; viewer draws WAVE_KEEP saltwater towns (model value at nearest sea point) +
  Seattle/Everett/Tacoma/Olympia names only; Oak Harbor -> Smith Island (48.321,-122.831, NDBC C-MAN sisw1). WA view order list in COAST_VIEWS.wa;
  pnwt own mode (coast adds after buoys); other town views (puget wwa ewa passes newa lm bc) use OWN_DEFAULT. Non-wave products unchanged.
  Buoys added: 46088 New Dungeness ("inner any"), 46267 Angeles Point, 46303 Southern Georgia Strait, 46120 Point Wells, 46118 Bellingham Bay
  ("inner": wa/puget/newa/wwa only), 46146 Halibut Bank ("sog": other views). QA qa_wa2.py 0 console errors; wa2_*.png.
- Branch west_coast_view: b3a9e4f on d2e319d (viewer.js?v=20261101p). Preview 89526d78: https://89526d78.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=wavemax&view=wc
  tools/fast/wave_views.py -> R2 static/wave_views.json, lut_ifs_wc.bin, base_wc.png, towns_wc.png (empty), key_ifs_{waves,wavemax,wavemax24}_wc_v1.png
  (+x2; built in /workspace/wave_scale_report/stwc, uploaded as NEW keys only; manifest.json NOT changed). Viewer merges wave_views.json (view after
  pnw, waveOnly: offered for waves/wavemax/wavemax24 only; non-wave product on wc falls back to pnw). Keys come from the view entry (keys[pid]).
  NOTE: the wc keys are drawn from the current scale tables; if a wave scale changes later, rerun wave_views.py with a new --ver and re-upload.
  QA qa_wc.py 0 console errors; wc_*.png.
- To ship (only on "Push"/"Deploy"): git checkout main && git merge --ff-only west_coast_view (brings d2e319d too) && push; deploy --branch=main.
  R2 files above are already in place (production 10e0714e ignores wave_views.json). Undo: git branch -D west_coast_view wa_wave_labels
  (R2 wc files can stay; unused).

# SHIPPED 11-01-2026 ~9:30 AM PST: COAST TOWNS -> production 10e0714e = origin/main db0b104 (prev a65466ef). See ROLLBACK_prod_10e0714e_20261101.md.
  db0b104 = coast_towns rebased onto 74b1d73, viewer.js?v=20261101n. QA qa_prod_coast.py 0 console errors; prod_*_coast*.png. Same known gaps as the preview.
# SHIPPED 11-01-2026 ~9:25 AM PST: BLUE-VIOLET scale + even legend numbers -> production a65466ef = origin/main 74b1d73 (prev 195878ab).
  See ROLLBACK_prod_a65466ef_20261101.md. Production reads models.ifs.products_v (_85w keys + kw); keep products_v. Manifest backup manifest_before_prod_bv.json.
  QA qa_prod_bv.py 0 console errors (wavemax na, wavemax24 pnw, waves wa, Studio, elows, t2m); prod_*_bv*.png.

# UPDATE 11-01-2026 ~9:25 AM PST: blue-violet LEGEND NUMBERS fixed, HIDDEN PREVIEW ONLY (Benjamin t1996u "I think the numbers need to be fixed here")
- Commit 74b1d73 on wave_scale_bv (after b34fd31; base main 21f7a24, no coast_towns). NOT pushed. viewer.js?v=20261101m, studio.js?v=20261101g.
- Preview ddb7b571 (branch "fast"): https://ddb7b571.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=wavemax&view=na (supersedes 847f9ccb). Prod still 195878ab.
- Fix: per-bin cell widths "kw" in the product (75-77.5 and 77.5-80 = half a cell each, all others 1), so 75-80 is one cell like the other 5 ft steps
  and 60/65/70/75/80/85 are evenly spaced, each on its color edge (no 77.5 label). Key images: fast_encode draws on display positions
  (cumulative kw) with spacing="proportional" (house_style.hbar got an optional spacing kwarg, default uniform = unchanged elsewhere).
  Studio colorbar() uses P.kw when present. Colors unchanged from b34fd31.
- Keys _85w (st85w), R2 models.ifs.products_v overwritten with _85w + kw (backup manifest_before_85w.json, local_manifest_before_85w.json),
  script publish_products_v_85w.py. QA qa_bv2.py 0 console errors; screenshots wave_scale_report/bv2_*.png.
- Ship / undo as in the 9:25 entry below (ff main to wave_scale_bv now brings 74b1d73 too).

# UPDATE 11-01-2026 ~9:25 AM PST: BRIGHT BLUE-VIOLET between hot pink and neon cyan, HIDDEN PREVIEW ONLY (Benjamin t1993u), NOT approved to ship yet
t1993u "the change from neon cyan at 75-80 is the harshest change. So one in between there like a bright blue violet would be good, let's try it."
- Branch wave_scale_bv, commit b34fd31 on main 21f7a24 (does NOT include coast_towns 64427a1). NOT pushed. viewer.js?v=20261101k (studio.js unchanged, f).
- Preview 847f9ccb (branch "fast"): https://847f9ccb.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=wavemax&view=na
  ("fast" alias now points here; coast towns preview efdd9469 unique URL still works). Production still 195878ab (canonical re-checked).
- wavemax + wavemax24 only: the 75-80 bin split at 77.5: 75-77.5 bright blue-violet #5b5bff, 77.5-80 neon cyan #00e5ff. Everything else as
  production (70-75 #ff1fa6, 80-85 #c8ff1a, over 85 #ffffff). Ticks unchanged (0,4,8,14,20,28,40,45,...,85; no 77.5 label). Bars use equal-width
  bins, so the 75-80 span is now two cells wide in the legend and Studio bar. Storm peak 79.98 ft: core is cyan ringed by blue-violet then pink.
- Keys static/key_ifs_<pid>_85v_<view>.png (44 incl. x2) built in /workspace/wave_scale_report/st85v (WX_KEY_PIDS=wavemax,wavemax24, --x2-only),
  R2 manifest models.ifs.products_v added (backup /workspace/wave_scale_report/manifest_before_85v.json; box copy merged, backup
  local_manifest_before_85v.json). Script publish_products_v_85v.py. viewer allProds reads products_v over products_t; production (v=i) ignores it.
- QA qa_bv.py 1440x900, 0 console errors on preview and production: wavemax na, wavemax24 pnw, waves wa (unchanged 0-40), Studio wavemax 16:9, t2m.
  Screenshots /workspace/wave_scale_report/bv_*.png, prodref_*.png, compare_neon_vs_bv.png (prod left, preview right, storm crop x4, legend crop x3).
- live_main checked back out on main (21f7a24); fast_deploy/site re-synced to main (v=20261101i).
- To ship (only on "Push" / "Deploy"): git checkout main && git merge --ff-only wave_scale_bv && push; build + deploy --branch=main.
  If coast_towns ships too: rebase one onto the other (both bump viewer.js: coast j, bv k; keep the higher, e.g. l) then deploy.
- Undo: delete models.ifs.products_v from the R2 manifest (and box copy), git branch -D wave_scale_bv.

# SHIPPED 11-01-2026 ~9:05 AM PST: production 195878ab = origin/main 21f7a24 (prev 4db69a55). See ROLLBACK_prod_195878ab_20261101.md.
Benjamin t1992u "Yes push and deploy, and add a couple more numbers to the scale, maybe every 5 feet instead of every 10".
Shipped: 03c7b8c Studio 85 tick, 65c9c8d buoy labels, b1ce7a6 max wave numbers every 5 ft 40-85 (keys _85t, R2 manifest models.ifs.products_t;
backup manifest_before_85t.json), 21f7a24 Studio max wave bar tick gap 0.3 em (16:9 shows 40,45,...,85; 9:16 shows every 10, no room).
Tick preview 46b2ed1b / cef754e0. Prod QA qa_prod_ticks5.py, 0 console errors; screenshots wave_scale_report/prod_*_ticks5*.png, ticks5_*.png.

# UPDATE 11-01-2026 ~9:15 AM PST: COAST TOWNS on the wave maps, HIDDEN PREVIEW ONLY (Benjamin t1990u), NOT approved to ship yet
- Branch coast_towns, commit 64427a1 on main 21f7a24 (NOT pushed). viewer.js?v=20261101j.
- Preview efdd9469 (branch "fast"): https://efdd9469.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=waves&view=wa
- viewer.js coastPlan / drawCoast / erasedTowns / seaVal (wave pids, ll grid only; other products untouched, t2m wa checked).
  WA view: adds La Push, Ocean Shores, Westport, Raymond; re-places Neah Bay, Forks, Aberdeen, Long Beach (cut out of the static town layer
  copy, placed again; must-place with fallback to old spot; their numbers read at the same pin as before). Long Beach + Ocean Shores over the ocean.
  WA buoys 46087, 46041, 46211, 46029 all show. Pacific NW: Ocean Shores, Long Beach, La Push on the land side (no other city labels there).
  Pacific NW tight: Ocean Shores, La Push added, Tacoma's name moved right so 46041 shows. New towns: model value at nearest sea point (<=1.5 cells).
- Gaps: Westport/Neah Bay don't fit in PNW + PNW tight (dots sit on buoys 46211/46087); Long Beach not added in PNW tight; 46087 still under
  Victoria in PNW tight; Astoria (old wave list) left out (OR town, crowding). Studio WA 16:9 header covers the top-left corner (46087), pre-existing crop.
- QA qa_coast.py: 0 console errors; screenshots wave_scale_report/coast_*.png (1600x1050 / 1600x1200 map canvas, Studio 1920x1080).
- To ship (only on "Push" / "Deploy"): git checkout main && git merge --ff-only coast_towns && push; deploy --branch=main. Undo: git branch -D coast_towns.

# UPDATE 11-01-2026 ~8:50 AM PST: BUOY labels on the wave maps, HIDDEN PREVIEW ONLY (Benjamin t1987u, t1988u, t1989u)
t1987u "Include known buoy locations off the coast, and have them show the wave height numbers, do the same for significant wave height";
t1988u "Just make them look like the other locations in the map"; t1989u "Make sure it doesn't look excessively crowded, the buoys I care
about the most are the ones right off the Washington coast in the PNW views".
- Branch buoy_labels, commit 65c9c8d on studio_85_tick 03c7b8c (NOT pushed). viewer.js?v=20261101h (studio.js stays e).
- Preview 3ba59b1a (branch "fast"): https://3ba59b1a.<PAGES_PROJECT>.pages.dev/?run=ifs/2026110100&f=300&prod=waves&view=pnw
  (earlier tries bc835df4, 8b5c40cf, 5c77ab2c, bc5fb51b superseded). Production still 4db69a55.
- viewer.js drawBuoys(): waves / wavemax / wavemax24 only (WAVE_PIDS, lat-lon grid), so Studio gets them too (it crops the viewer map).
  56 fixed buoys in tools/fast/site/buoys_ndbc.json (inlined as BUOYS), coordinates from NDBC activestations.xml (copy in
  /workspace/wave_scale_report/activestations.xml). Order = priority: WA set first (46041 46029 46087 46005 46089 46050 46002 46211).
  Style = region city labels: 3.2 pt dark dot with white edge, "Buoy 46041" 600 8.5 pt #1b1d22 on 2.4 pt white halo, then bold 800 9.5 pt value
  (3 pt halo). Value = MODEL value of the displayed field at the buoy (bilinear if 4 sea points, else nearest sea point), rounded ft. NOT observations.
  Placement right / left / above / below / diagonals (+ extra 12 pt nudges for WA buoys); dropped if it touches a city label (cities keep
  priority), another buoy or the map edge. Spacing: 30 pt from drawn buoys for WA buoys, 48 pt for others; North America view shows only the
  17-buoy "wide" set at 60 pt.
- Known: in Pacific NW tight, 46041 and 46087 sit under the Tacoma / Victoria city labels and are left out (46029, 46211 show); in the WA view
  46087 sits under the Neah Bay label. City labels are a static layer, so moving them needs an encoder rebuild.
- QA qa_buoys.py: 0 console errors on waves + wavemax na/pnw/pnwt/wa, wavemax24 pnw, t2m pnw (no buoys), Studio wavemax storm + waves pnw 16:9.
  Screenshots /workspace/wave_scale_report/buoys_*.png (map canvas at real size 1600x1050 / 1600x1200, Studio 1920x1080).
- To ship (only on "Push" / "Deploy"): git checkout main && git merge --ff-only buoy_labels (brings studio_85_tick too) && push; deploy --branch=main.
- Undo: git branch -D buoy_labels.

# UPDATE 11-01-2026 ~8:35 AM PST: Studio "85" tick label fix, HIDDEN PREVIEW ONLY (Benjamin t1986u "Yes fix the tick label")
- Branch studio_85_tick, commit 03c7b8c on main f8f0ffc (NOT pushed). studio.js colorbar(): the top tick (t == last level) that used to be skipped
  next to 80 is now drawn left-aligned starting just past the bar's right end (tick mark at the end); other ticks unchanged; still skipped if it
  would touch. studio.js?v=20261101e; viewer.js unchanged (v=20261101g). Max height label (above the bar) unaffected.
- Preview 05d3f29a (branch "fast"): https://05d3f29a.<PAGES_PROJECT>.pages.dev/studio.html?run=ifs/2026110100&f=300&prod=wavemax&view=na
  (68b6dc16 = first try, label 4 px tighter, superseded). Production still 4db69a55.
- QA qa85tick.py: studio wavemax + wavemax24 storm, 16:9 1920x1080 + 9:16 1080x1920 canvases, 0 console errors.
  Screenshots /workspace/wave_scale_report/studio_{wavemax,wavemax24}_storm_85tick_{16x9,9x16}.png.
- To ship (only on "Push" / "Deploy"): git checkout main && git merge --ff-only studio_85_tick && push; build + deploy --branch=main.
- Undo: git branch -D studio_85_tick.

# SHIPPED 11-01-2026 ~8:25 AM PST: NEON (f8f0ffc) pushed to origin/main and deployed to production 4db69a55 (prev bb67543f). See ROLLBACK_prod_4db69a55_20261101.md.

# UPDATE 11-01-2026 ~8:25 AM PST: NEON EXAMPLE (85n) as a SECOND hidden preview; saved 85d kept as-is
Benjamin 8:12 AM (t1983u): "This is closer to what I'm wanting. Should we add more neon style colors for the highest waves, to make them really jump
out at us? Save this one, but make me an example... highest waves almost jump off the scale colors".
- SAVED: tag wave_scale_85d_saved = 369db87 (= main HEAD, not pushed). Preview 323af52e untouched, still viewer.js?v=20261101f, reads products_p (_85d keys);
  re-checked after the neon publish: 85d colors, over #f3ebff, 0 console errors.
- NEON: branch wave_scale_neon, commit f8f0ffc on 369db87 (NOT pushed). viewer.js?v=20261101g; allProds also reads models.ifs.products_n (over products_p).
  Preview 341eb6bf (branch "fast"): https://341eb6bf.<PAGES_PROJECT>.pages.dev  (the "fast" branch alias now points here; 323af52e unique URL still works)
  Colors: 0-55 ft same as 85d; 55-60 #2b1873 deep indigo trough; 60-65 #9b1cff electric violet; 65-70 #e01cff neon magenta; 70-75 #ff1fa6 hot pink;
  75-80 #00e5ff neon cyan; 80-85 #c8ff1a electric lime; over 85 #ffffff. Ticks unchanged. Land tan, Max height label kept.
- Keys static/key_ifs_<pid>_85n_<view>.png (44) built in /workspace/wave_scale_report/st85n, R2 manifest models.ifs.products_n added
  (backup manifest_before_85n.json; box copy merged, backup local_manifest_before_85n.json). Script publish_products_n_85n.py. No re-encode.
- QA 1440x900 (qa85n.py; qa_saved_prod_85n.py) 0 console errors. Screenshots /workspace/wave_scale_report/*_85n*.png, compare_saved85d_vs_neon_85n.png.
- live_main checked back out on main (369db87) and fast_deploy/site re-synced to main (v=20261101f), so a later deploy does NOT carry neon by accident.
  To ship NEON instead: merge/ff main to wave_scale_neon (+ for production also copy products_n into products_p or ship as is; production ignores both today).
- Undo neon: delete products_n from the R2 manifest (or restore manifest_before_85n.json's models.ifs), git branch -D wave_scale_neon.

# UPDATE 11-01-2026 ~8:20 AM PST: START OVER from the 60 ft look (85d), HIDDEN PREVIEW ONLY (supersedes 85c below)
Benjamin 8:05 AM (t1980u, screenshot of the 60 ft preview): "let's start over, as mentioned, I like the color scale here. Basically keep the same
order of colors, and just add a couple more transitional shades up to the max wave height of 85". 8:06 AM (t1981u) other site's scale for ideas only
(not copied; only idea used: distinct transitional shades at the high end).
- Local commit 369db87 on top of 380c05d (NOT pushed; origin/main still c2a1e39). viewer.js?v=20261101f (studio.js unchanged).
- Preview deploy 323af52e (branch "fast"): https://323af52e.<PAGES_PROJECT>.pages.dev  (supersedes 9e7dbc6c)
- wavemax + wavemax24: original 0-40 bins/colors unchanged (0,1,2,3,4,5,6,8,10,12,14,16,18,20,24,28,32,40:
  #284ba2 #2869bc #2886ca #28a1d0 #2ab3c0 #30ba9e #50c369 #9bd241 #d2d23a #e6be34 #eea731 #eb8c30 #e8712e #de5533 #d03740 #be264e #a02167),
  then 5 ft steps: 40-45 #841f7f, 45-50 #6c2595, 50-55 #512da0, 55-60 #6f46b4, 60-65 #8563ca, 65-70 #9d81db, 70-75 #b69feb, 75-80 #cdbcf3,
  80-85 #e2d6fa, over 85 #f3ebff (same near-white lilac as the 60 ft scale). Land tan #ece8df on both. Ticks 0,4,8,14,20,28,40,50,60,70,80,85.
  waves stays 0-40. Max height label kept.
- Keys static/key_ifs_<pid>_85d_<view>.png (44) built in /workspace/wave_scale_report/st85d; R2 products_p = 85d (backup manifest_before_85d.json),
  box manifest merged (backup local_manifest_before_85d.json). Script publish_products_p_85d.py. No re-encode.
- QA 1440x900 0 console errors (qa85d.py): wavemax/wavemax24 storm + PNW + plain, waves, Studio. Production bb67543f re-checked (v=20261101b, 0-40, 0 errors).
  Screenshots /workspace/wave_scale_report/*_85d*.png. Known nit: Studio's bar omits the "85" tick label (ends at 80); viewer legend shows 85.
- Undo: git reset --hard 380c05d and put manifest_before_85d.json products_p back.

# UPDATE 11-01-2026 ~8:15 AM PST: colors redone (85c), HIDDEN PREVIEW ONLY
Benjamin 7:57 AM (t1979u): "I liked the way it was where the nearly white color was the highest wave, the red colors look too close to the red
colors before the blue/purple, so maybe just have some pink after blue then. Maybe have the calmest, shortest colors be grey shades."
- Local commit 380c05d on top of 2ed7957 (NOT pushed; origin/main still c2a1e39). viewer.js?v=20261101e (studio.js unchanged at d, holds no colors).
- Preview deploy 9e7dbc6c (branch "fast"): https://9e7dbc6c.<PAGES_PROJECT>.pages.dev  (supersedes 88544077)
- Same bins (0,5,10, then 2.5 ft to 85), ticks 0..80 + 85, Max height label, wavemax24 tan land. One color per bin:
  grey 0-5 #b9bec5, 5-10 #979ea7, 10-12.5 #7a828d, 12.5-15 #5f6773 | blue 15-30 #173a7a #1f4f9e #2a66c0 #3a80db #559ced #7ab8f7 |
  indigo/violet 30-45 #2c288c #4433b6 #5f40d6 #7d56e8 #9b70f2 #b98df8 | purple/magenta 45-57.5 #6c2290 #8c29ad #ab34c4 #c843d2 #e05ad6 |
  pink 57.5-70 #e852b0 #f06cb4 #f589c6 #f9a6d6 #fcc2e4 | lilac->near-white 70-85 #e2aef4 #d6bcfb #dccaff #e6d8ff #efe5ff #f6f0ff | over 85 #ffffff.
  Adjacent-step CIE76 dE >= 6.8 (smallest 80->82.5 near-white).
- Keys static/key_ifs_<pid>_85c_<view>.png (44 incl. x2) built in /workspace/wave_scale_report/st85c, uploaded; R2 manifest models.ifs.products_p
  = 85c (backup /workspace/wave_scale_report/manifest_before_85c.json); box manifest merged (backup local_manifest_before_85c.json).
  Script publish_products_p_85c.py (run with /workspace/.venv-r2/bin/python, CLOUDFLARE_ACCOUNT_ID set). No re-encode.
- QA 1440x900, 0 console errors: wavemax/wavemax24 storm + PNW + plain, waves (0-40 unchanged), Studio. Production bb67543f re-checked
  (viewer.js?v=20261101b, 0-40 old keys, 0 errors). Screenshots /workspace/wave_scale_report/*_85c*.png.
- Undo colors only: git reset --hard 2ed7957 and put manifest_before_85c.json products_p back.

# Max wave height scale 0-85 ft (finer steps) + "Max height: NN ft": HIDDEN PREVIEW ONLY (11-01-2026 ~7:55 AM PST)
Supersedes PREVIEW_wave_scale_60ft_20261101.md. Benjamin 11-01: 7:38 AM (t1975u) "make the scale go to 85ft, going to have to get creative";
7:41 AM (t1976u) "Make there be more increments in the scale, I don't care as much about the first 10 feet"; 7:43 AM (t1977u) "Add a 'max height:80ft'
just underneath the bottom right of the graphic ... studio mode, include that somewhere on the canvas"; 7:44 AM (t1978u) true max, not a bin.
- Local commits on live_main (NOT pushed): d333803 (60 ft) -> 2f885b9 (85 ft ramp, wavemax24 land tan, viewer.js?v=20261101d) -> 2ed7957 (Max height label, studio.js?v=20261101d).
  origin/main still c2a1e39.
- Preview deploy 88544077 (branch "fast"): https://88544077.<PAGES_PROJECT>.pages.dev  (earlier 85 ft-only preview f517ea9b, 60 ft d6d4ada3)
- Production unchanged: canonical bb67543f (viewer.js?v=20261101b, 0-40 scale, old key names; re-checked after the manifest change, 0 errors).
Scale (wavemax + wavemax24 only; Significant Wave Height `waves` keeps 0-40): levels 0,5,10 then every 2.5 ft to 85 (32 bins), over 85 white.
  anchors 2.5 #22408f, 7.5 #2a7cc4, 10 #26aecb, 15 #36c08c, 20 #96cf3a, 25 #f0d23a, 30 #f5982e, 35 #e4502c, 40 #c21e3c, 45 #8e1e78, 50 #5c1fa0,
  55 #3e2ca8, 60 #7a4cff, 65 #b48aff, 70 #ffa6d8, 75 #ff3d9a, 80 #c4005a, 85 #5c0a2e; ticks 0,10,...,80,85. Keys static/key_ifs_<pid>_85b_<view>.png.
  (2 stray _85_ key files from an interrupted first upload exist on R2, unused.)
Land: wavemax24 now under=#ece8df (tan) like waves/wavemax (was black).
Max height label: viewer.js draws "Max height: NN ft" right-aligned under the map's bottom-right corner (true grid max over the view rows/cols,
  rounded); Studio draws it right-aligned above the color bar end (max of drawn values inside the frame crop). MAXH_PIDS = wavemax, wavemax24.
R2 manifest: models.ifs.products_p = 85b versions (backup before: /workspace/wave_scale_report/manifest_before_85.json); box copy
  fast_deploy/data/manifest.json merged (backup: /workspace/wave_scale_report/local_manifest_before_85.json). Script publish_products_p_85.py.
To ship (only on his "Push"/"Deploy"): git push (fast-forward 3 commits); deploy fast_deploy as usual.
Undo: git reset --hard c2a1e39 (local); put back manifest_before*.json products_p or pop it (production ignores it).

## SHIPPED 11-01 ~10:35 AM PST: marine names (t2008u, ship t2009u)
Commit e8774d6 (branch marine_names, fast-forwarded to main, pushed f1e96cc..e8774d6). Hidden preview 7abbfe39 -> production d9c22691 (previous 20c07c0d).
Labels: Possession Sound, Elliott Bay, Commencement Bay (name only); Admiralty Inlet, Tatoosh Island (with numbers); Birch Bay stays.
Fit: all show on WA, Puget Sound, Passes, Studio WA. Pacific NW tight: water names placed last at regular size so Ocean Shores / La Push stay;
Commencement Bay + Possession Sound don't fit there (Elliott Bay does). Western WA: Elliott Bay doesn't fit. Pacific NW / West Coast: Tatoosh Island
doesn't fit (same as before). Rollback: ROLLBACK_prod_d9c22691_20261101.md. QA prod_mar_*.png, 0 console errors.

## UPDATE 11-01 ~10:45 AM PST: trim towns on Western WA + Puget Sound wave views (t2011u) - HIDDEN PREVIEW ONLY, not pushed/deployed
Branch wave_trim, commit ec20c3e (on main e8774d6), viewer.js?v=20261101t. Preview: https://058553b6.<PAGES_PROJECT>.pages.dev (production still d9c22691).
WAVE_DROP in viewer.js (all wave products, viewer + Studio; other views unchanged).
Western WA removed: Bremerton, Poulsbo, Coupeville, Friday Harbor. Kept: Birch Bay, Anacortes, Smith Island, Admiralty Inlet, Port Angeles, Tatoosh Island,
  Possession Sound, Elliott Bay (fits now), Commencement Bay, Ocean Shores, Westport, Long Beach, Cannon Beach + buoys.
Puget Sound removed: Bremerton, Poulsbo, Port Orchard, Port Ludlow. Kept: Port Angeles, Admiralty Inlet, Kingston, Edmonds, Mukilteo, Bainbridge Is.,
  Gig Harbor, Possession Sound, Elliott Bay, Commencement Bay + buoys.
Screens trim_*.png. To ship (only on his Push/Deploy): ff main to ec20c3e, push, deploy. Undo: drop the commit.

## SHIPPED 11-01 ~10:47 AM PST: wave_trim ec20c3e (t2013u). Pushed e8774d6..ec20c3e; production f40d3ba9 (previous d9c22691). Rollback: ROLLBACK_prod_f40d3ba9_20261101.md. QA prod_trim_*.png, 0 console errors.
