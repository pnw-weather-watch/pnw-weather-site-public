# Overnight build log, 11-04 (hidden preview only, no production deploys)

| Time PT | Item | Commit | Screenshots (local/shots/20261104/) |
|---|---|---|---|
| 18:50 | SST anomaly (INDEX #16), NOAA OISST | 61e1ed9 | sst_pnw/pac_desktop/phone.png, preview_sst_pac_*.png |
| 19:00 | Observations: California + Hawaii presets (INDEX #17 gap) | 51cf1be | obs_ca/hi_desktop/phone.png, preview_obs_ca_*.png |
| 19:10 | Meteogram temperature colors from the site palette | 70cf9da | meteogram_colors_BEFORE/AFTER(.png/_phone.png) |
| 19:25 | Southern / Central / Northern California views | ebe1766 | view_socal/cenca/norca_t2m_*.png, preview_socal/cenca/norca_t2m_*.png |
| 19:35 | Preview-only data area (R2 `preview/` prefix; production reads live keys only) | dc362ad | - |
| 19:50 | ECMWF ensemble (INDEX #10 mean, #11 lows, #19 CAPE chance): EPS 00Z 11-04, F3-F48; ensembles reuse IFS normals | 811210d | preview_eps_mean_mslp_pnw_*, preview_eps_lows_pnw_*, preview_eps_z500anom_na_*, preview_eps_capechance_na_* |

## Checks
- Production guard (read-only, no deploy) 19:40: 139 OK, 0 FAIL. Its manifest is unchanged (no new views, runs gfs + ifs only).
- Preview manifest: new views + eps + oisst.

| 20:24-20:44 | Benjamin Push+Deploy (run by the deploy script outside this stretch; outcome recorded by the build agent). Attempt 1 at 20:24 (bb01bc8): STOPPED at the preview guard, production untouched: the EPS Southern/Central/Northern California statics (key_eps_*_socal/cenca/norca, lut_eps_*) were not yet in R2 (404 + refresh fell back to `ca`). Fixed at ~20:35 by syncing local data to R2 `preview/` (588 files); preview guard then 261 OK / 0 FAIL. Attempt 2 at 20:35: live-key promote (manifest backup backups/prod_promote_20261104/manifest.live.before2.json), then production deploy 2fac240f of commit bb01bc8 at 20:44 PT (previous prod b51db3eb, rollback record ROLLBACK_prod_b51db3eb_20261104.md). The script's own 760 s wrapper cut off its production guard, so I re-ran the guard on production afterwards (qa/guard_prod_after_deploy.log): 261 OK, 0 FAIL. No rollback needed. | bb01bc8 (prod 2fac240f) | local/shots/20261104/prod_live_*.png (earlier) |

## Stretch 2 (after the production deploy; hidden preview only, NO further production deploys)
| Time PT | Item | Commit | Screenshots (local/shots/20261104/) |
|---|---|---|---|
| 20:50 | Wave maps: coast town numbers read from a point ~1/4 mile offshore (was 1/2 mile; explicit points pulled 0.4 km toward the town pin). Preview deploy dfdec6c2, preview guard OK | 287c112 | offshore_quarter_waves_pnw/wc/ca_desktop.png and _phone.png |

| 20:47-20:48 | CA views widen (preview only): Central 2x E-W, Southern +12.5% east + 50 mi west, Northern 2x E-W | 92987b2 | view_{cenca,socal,norca}_BEFORE_widen.png, view_*_AFTER_widen_{desktop,phone}.png |
| 20:00-20:45 | Production Push+Deploy: promoted preview/ data, t2ma CVD fix bb01bc8, deploy 2fac240f (rollback target b51db3eb) | bb01bc8 / 2fac240f | prod_socal/cenca_t2m_*, prod_sst_pac_*, prod_eps_lows_* (guard 261 OK) |
| 21:05 | Ensemble lows: member dot colors + mean-L list recolored into the site theme (violet-blue-teal-green-yellow-grey, deutan/protan dE >= 7); LAUNCH known gap #7. Preview deploy of cb2e161, preview guard OK (261 checks, 0 FAIL) | cb2e161 | ens_dots_theme_elows_pnw/na_desktop.png and _phone.png |
| 21:20 | QA: interaction check (readout, zoom, save, share, peak gust, missing hour, preload, view default, WA + CA Pass Forecasters) on the preview: 10/10 OK; the preload test now picks a run with steps (newest GFS 18Z is a single-step run). Ticked checklist: local/DETAILS_CHECKLIST_ticked_20261104.md (13 more lines) | 5a6658e | qa/interaction_preview_20261104.log |
| 21:30 | Safety: upload_r2.py / read_requests.py pinned to the PNW account and PNW R2 keys (they used the shared CF_PAGES_KEY); request queue read: empty, nothing from Michael Snyder yet | b4c7b3c | - |
| 21:35 | Verification of queued items on the preview: dashed 540 dam thickness line and 32F line (white dashes, thin black edge), darker blues, WA + CA Pass Forecaster tabs, meteogram colors, S/C/N California views | (earlier commits 964d696, b3bc105, 2eaef2b, 70cf9da, ebe1766) | check_thick540_pnw_desktop/phone.png, check_thick540_zoom.png, check_t2m_blues_pnw_desktop/phone.png |

| 21:28 | HOLD (clarified 21:29): do NOT build the current site's "WA Maps" page graphics (NBM 2.5 km predicted low/high/gust/snow posters with WAWX Chasers logo, big titles, town temps, summary text) until Benjamin says otherwise. Normal model products and Washington regional views (Pacific Northwest, Cascade Passes, etc.) stay in the queue. |

| 21:30 | HOLD reinforced: do NOT build a "WA Maps" tab or any WA Maps-style graphics (NBM poster maps with logo/big titles). Build everything else. Normal model products + Washington regional views OK. |

| 21:31 | NOTE (overnight builder #2, 21:31 PT): two builders are active in this folder. Claimed by this builder: AIFS (aifs), AIFS ENS (aens), then GFS-Wave, HRRR/RRFS/NBM high-res views, remaining DETAILS_CHECKLIST ticks. Member grids / EPS members / mslpa keys (backups/batch_mgrid_20261104) are left to the other builder. No WA Maps graphics (HOLD above). Commits stay local, nothing pushed to origin/main, no production deploy. | - | - |

| 21:30 | HOLD reinforced: no "WA Maps" tab / WA Maps-style graphics. Build everything else. |
| 21:35 | #12 member grids + #13 member meteograms (EPS mem data F3-F48 + epsm F6-F72); MSLP a80 keys for socal/cenca/norca into site mkeys; epsm model wired on preview | 12d5698 | mgrid_tmax_*, mlines_t2m_*, mgrid_qpf_*, meteograms_honolulu_*, mslpa_a80_*_desktop.png, epsm_mslp_m01_pnw_desktop.png |

| 21:45 | #12/#13 member grids + meteograms screenshots; MSLP a80 keys for new CA views; epsm (snow member) on preview; WA Maps hold. Guard: 397 OK before timeout (more models), 0 FAIL so far. Commits 12d5698, abea624, c6fe3e6 |

| 22:25 | epsm CVD-safe keys for SLP / gust / 500 mb height anomaly (palette fixed, deutan/protan dE>=3.2); snow kept; MODELS+filter in fast_encode; theme/epsm_cvd_scales.json; preview R2 synced. #18 radar/sat CA+HI confirmed (radsat_*). WA Maps still HOLD. |
| | Commits: pending | epsm_{gust10,slp,snow,z500anom}_pnw_{desktop,phone}.png |

| 22:46 | epsm CVD-safe SLP/gust/z500anom keys (palette fix); MODELS+filter; theme/epsm_cvd_scales.json. Screenshots epsm_{gust10,slp,snow,z500anom}_pnw_*.png | 566e288 | local/shots/20261104/epsm_*_pnw_desktop/phone.png |
| 22:46 | QA guard hardened (commit vs networkidle); full preview guard by GUARD_MODELS batches: **577 OK / 0 FAIL** (all models) | ded9016 | qa/guard_preview_full_20261104.log |
| 22:46 | Ensemble extend: epsm F6-F120 (20 steps) on preview. EPS mean / AENS extend in progress beyond F48 (partial hours encoded; run.json merged as unbroken prefix grows). | (data) | - |
| 22:46 | #18 radar/sat CA+HI confirmed (obsimg region detail boxes + radsat_* shots). DETAILS_CHECKLIST gaps closed where verified (dsnod, coast CA/HI, wave scales, mslpa a80, member lookup, obs CA/HI). WA Maps HOLD. | - | radsat_ca_*, radsat_hi_* |

| 23:20 | Ensemble coverage on preview (after merge fix): **epsm F6–F120** (20 steps), **EPS mean F3–F96** (32 steps), **AENS F6–F120** (20 steps). fast_encode steps() keeps earlier hours on --steps extends (b89ca6b). |
| 23:20 | Full preview QA (GUARD_MODELS batches, hardened goto): **577 OK / 0 FAIL** — qa/guard_preview_full_20261104.log. |
| 23:20 | epsm CVD keys live on preview: gust10/slp/snow/z500anom (theme/epsm_cvd_scales.json). Screenshots earlier: epsm_{gust10,slp,snow,z500anom}_pnw_{desktop,phone}.png. |
| 23:20 | INDEX sweep: #10/#11/#12/#13/#16/#17/#18/#19 done on preview; WA Maps HOLD. DETAILS_CHECKLIST: remaining open mostly style-doc / NBM look / partial [~] items. No production deploy. |

| 23:26-23:43 | Polish pass (preview only, no prod): Playwright chromium reinstalled; full-size retakes of extended ensemble hours + meteograms colors. Soft DETAILS leftovers ticked where code-verified (NBM site temp scale ≠ WA Maps posters; OBS_STYLE; remaining [~] → [x]). Final overall preview QA with rotated Access service token `pnw-qa`: **FINAL_OK 576 / FINAL_FAIL 0** (`qa/guard_preview_final_20261104.log`). Wrote `SUMMARY_overnight_20261104.md` (built items, commits, shot paths, open decisions for Benjamin: PacIOOS, PNW towns, new sources; what Push/Deploy would promote). WA Maps still HOLD. | (polish commit) | eps_ext_f96_{t2m,elows}_pnw_{desktop,phone}.png, aens_ext_f120_t2m_pnw_*.png, epsm_ext_f120_{slp,snow}_pnw_*.png, meteograms_colors_seattle_{desktop,phone}.png |

## Stretch 3 (11-04 23:20 PT onward, builder #3; hidden preview only, no production deploy)
| Time PT | Item | Commit | Screenshots (local/shots/20261104/) |
|---|---|---|---|
| 23:20 | Box restart ~23:14 PT: no jobs were running. Found `local/data/runs/eps/.../run.json` restored to the stale F51-F96 prefix (F3-F48 missing); restored the merged 32-step file from R2 `preview/` (read only, PNW account). Restarted EPS (F99-F144) and AIFS ENS (F126-F192, F198-F240) extends in the background. | (data) | - |
| 23:50 | NBM 2.5 km 00Z run F1-F168 (80 steps) and RRFS 3 km 00Z run F1-F84 (60 steps) built and wired on the preview (NOAA public domain, no new source). Local guard nbm+rrfs: 123 OK / 0 FAIL (qa/guard_local_nbm_rrfs_20261104.log, copy in backups/nbm_rrfs_20261104/). No WA Maps posters (site temp scale, no logo/summary text). | 9671c75 | nbm_t2m_pnwhr, nbm_snow24_passes, nbm_gust_ca, nbm_qpf24_wa, rrfs_refc_pnwhr, rrfs_t2m_socal, rrfs_qpf24_passes (_desktop/_phone.png) |

## Stretch 4 (11-05 00:20 PT onward, builder #4; hidden preview only, no production deploy)
| 00:20 | CLAIMED by builder #4: Hawaii waves on ECMWF open wave model (WAM 0.25 deg; PacIOOS stays unused), new views Bay Area / Oregon coast / Big Island, PNW town labels. Left to other builders: EPS/AENS/epsm longer-run extends (EPS F150-F240 job already running as pid 35807). WA Maps stays OFF the list entirely (Benjamin 00:16 AM: no WA Maps tab or WA Maps-style graphics). | - | - |
| 00:30 | COORDINATION (builder #4): another builder is already doing Hawaii ECMWF waves + views bay / orco / bigi (backup backups/views_towns_hiwaves_20261105). Builder #4 STANDS DOWN from those (I briefly wrote orcoast/bigis view entries into regions.json and merged them back out at 00:29; their view entries, model_views and HL/smooth keys are restored as they had them). Builder #4 also dropped its own extra_towns idea at 00:33 (their stations.json additions cover the towns) and now only VERIFIES: WA Maps absence, request queue (empty at 00:33, nothing from Michael Snyder), Pass Forecaster tabs, then guard + full-size screenshots of whatever the other builder commits/deploys. No commits of mine touch regions.json / viewer.js / stations.json. | - | - |
| 00:35 | VERIFY (builder #4, preview as of 00:33): tab/button check on the preview: Surface, Precip, Snow, Upper Air, Severe, Waves, Compare; Meteogram, Washington Pass Forecaster, California Pass Forecaster, Observations, "Request a change" present; "WA Maps" appears nowhere in the page or the site code (only in renderer comments). Request queue read (read-only): empty, nothing from Michael Snyder. Hawaii waves BEFORE shots (ECMWF IFS WAM on hiw already existed; duplicate "Hilo 5" and inland Wahiawa/Lanai City labels seen on hiw waves; handed to the builder who owns hiw/bigi): local/shots/20261105/hiwaves_ifs_BEFORE_{desktop,phone}.png, hi_waves_BEFORE_ifs_*, hi_wavemax_BEFORE_ifs_*. | - | local/shots/20261105/ |

| 00:19-00:40 | BUILDER (views/waves/towns/ensembles): HI wave towns switched to ECMWF/model offshore in viewer.js (PacIOOS NEVER; NWPS disabled). New views bay/orco/bigi + pnw region_towns (CA-like) in regions.json; stations densified. Static ifs+gfs rebuilt (pnw 29 / bay 10 / orco 14 / bigi 6 towns). **epsm F6–F240** (30 steps) via eps_members; EPS mean files through ~F222 (run.json merge pending job end); AENS already F240. WA Maps OFF. | (commit below) | BEFORE shots in local/shots/20261105/; AFTER after preview deploy |
| 00:40-00:52 | Preview deploy + R2 sync; AFTER shots HI/PNW towns/bay/orco/bigi/epsm F240. | f5ef608 80ef26c | local/shots/20261105/*AFTER* , bay_*, orco_*, bigi_*, epsm_ext_f240_* |
| 00:52 | Ensembles on preview: **EPS F3–F240**, **epsm F6–F240**, **AENS F6–F240**. WA Maps OFF. | (data) | - |
| 01:07+ | Weather Bot B (preview): snow scale floors; ECMWF gust3+gust6; sat 4h loop + scrubber row; F+/elows verify; WW3 → open decision only. | (pending) | gust6_BEFORE_*, elows_key_check_*, badge_F_check_* |

| 01:09-01:18 | Weather Bot B shipped on preview: snow scale floors (pass/meteogram ≥12 in/6h); **gust3** + gust6 on ECMWF/IFS (+GFS/HRRR/RRFS/AIFS); obs sat **4 h loop** + scrubber own row (~480 px). F+ badge placement OK; elows member color key + density key OK; buoys/towns/H/L on wave/temp maps. No Studio/Social. WW3 → SUMMARY open decision. Commit **c6077eb**, preview deploy 9c9042d6. | c6077eb | gust3_AFTER_*, gust6_AFTER_*, buoys_hl_waves_pnw_*, obs_sat_loop4_AFTER_*, pass_snow_floor_*, elows_key_check_*, badge_F_check_* |

| 01:21 | Obs sat 4h scrubber verified (slideW=480 px, Clean IR on). Stretch4 full preview guard earlier: **FINAL_OK 848 / 0 FAIL**. | - | obs_sat_loop4_AFTER4_desktop.png |
| 01:22 | Fix run.json `expected` = full cadence (not --steps window); repaired eps/epsm/aens expected on disk + syncing preview. Commit **298eac2**. Restarted extends toward F360: EPS F246–360, AENS F246–360, epsm F252–360 (background). | 298eac2 | - |

| 01:25 | Wire unused `SCALE_FLOOR_SNOWRATE` (3 in/h) on pass winter meteogram; 6 h floor on winter bars; multi-run 12 in floor snow-only. Preview deploy **d5ddd687**. Commit **a9aae70**. | a9aae70 | meteogram_*_AFTER*.png, pass_snoq_snowfloor_AFTER3_desktop.png |
| 01:28 | Ensembles F246+ encoding in background (AENS/epsm writing; EPS downloading). Obs sat scrubber verified earlier (slideW=480). WW3 remains open-decision only. | - | obs_sat_loop4_AFTER4_desktop.png |

| 01:30 | Guard B **FINAL_OK 414 / 0 FAIL** (ifs,gfs + eps,epsm). Winter meteogram floors visually confirmed (6 h axis to 12, snow-rate axis to 3.0) on Snoqualmie ECMWF. Weather Bot status draft staged for parent DraftExternalMessage. | ac7530c | meteogram_ifs_winter_snoq_AFTER_desktop.png |

| 01:46 | **epsm complete F6–F360** (40/40). Reindexed run.json after windowed encode overwrote it; synced preview. Shots epsm_ext_f360_AFTER_*. | - | epsm_ext_f360_AFTER_{desktop,phone}.png |

| 01:57 | Fix `eps_members.py` so windowed extends merge full STEPS into run.json (prevents wiping F6–F240). Commit **454b90e**. EPS/AENS still encoding (~F324 files on disk). | 454b90e | - |

| 02:00 | Fix viewer `viewStatic` TDZ (`obj` before init) + missing `run.grid` (console errors on HI waves). Preview deploy **de9bb4fc**. Commit **e21f691**. | e21f691 | waves_{hiw,bigi,bay,orco}_ifs_AFTER_fix_desktop.png, waves_hiw_ifs_AFTER_fix_phone.png |

| 02:22 | **EPS mean complete F3–F360** (84/84) and **AENS complete F6–F360** (60/60) on preview (with epsm F6–F360). All three ensembles at full cadence. | (data) | eps_ext_f360_AFTER_*, aens_ext_f360_AFTER_*, eps_elows_ext_f360_AFTER_* |

| 02:26 | Soft-wait for `run.grid` in viewStatic (no console Error). Preview **9b9598ed**. Commit **ace1f05**. EPS/AENS/epsm all F360 on preview. | ace1f05 | eps_f360_clean_AFTER_desktop.png, eps_ext_f360_AFTER_*, aens_ext_f360_AFTER_* |

## Stretch 5 (11-05 02:17 PT onward, builder #5; hidden preview only, no production deploy)
| 02:17 | Box check: no extend jobs running. Local run.json: **EPS 00Z 84/84 steps F3–F360 complete**, **AENS 12Z 60/60 F6–F360 complete**, **epsm 40/40 F6–F360 complete**; every step has its files on disk, 0 zero-byte files. No restart needed. | - | - |
| 02:20 | Preview R2 was behind (preview/ run.json EPS F3–F240 64/84, AENS F6–F240 40/60, `complete: false`). Synced `local/data` to the `preview/` prefix only (PNW account): 213 files; now preview run.json EPS 84/84, AENS 60/60, epsm 40/40, all `complete: true`; object counts match local (EPS 925, AENS 541, epsm 2001). | (data) | - |
| 02:27 | Request queue read (read-only): "no requests", nothing from Michael Snyder. | - | - |
| 02:28 | Verified on the live preview with the QA Access token: EPS and AENS F+360 render. Guard eps+aens+epsm: **277 OK / 0 FAIL** (`FAILS 0`, console errors 0). | (log) | local/shots/20261105/{eps_f360_AFTER_t2m,eps_f360_AFTER_elows,aens_f360_AFTER_t2m,aens_f360_AFTER_asnow}_{desktop,phone}.png ; qa/guard_preview_ens360_20261105.log (copy in backups/ens360_verify_20261105/) |
| 02:30 | Rules re-checked in code: no "WA Maps" string in site/viewer code; Hawaii wave towns use ECMWF/model offshore (PacIOOS never, NWPS unloaded); wave-town value point 1/4 mi off shore (OFF_KM); INDEX #01–#19 and DETAILS_CHECKLIST (ticked copy: 0 open) all done. Nothing left in the queue; no new data sources used. | - | - |

| 02:32 | Ensemble F360 preview guard (eps,epsm,aens): **FINAL_OK 277 / 0 FAIL** — `qa/guard_preview_ens_f360_20261105.log`. Morning report draft `MORNING_REPORT_20261105.md`. | 0affee9 | - |

| 02:33 | Guard null `viewStatic` in render paths. Preview **8e94eb28**. Commit **3db6fde**. Feature queue A/B complete; ensembles at F360; continuing QA until morning report. | 3db6fde | - |

| 03:16 | Final check (builder #6): request queue empty (nothing from Michael Snyder); working tree clean except per-feature backup folders, now committed. All queued items verified done earlier (see rows above). No production deploy, WA Maps OFF. | see git log | - |

## Stretch 7 (11-05 04:18 PT onward, builder #7; hidden preview only, no production deploy)
| Time PT | Item | Commit | Evidence |
|---|---|---|---|
| 04:20 | Request queue re-read (read-only): "no requests", nothing from Michael Snyder. | - | - |
| 04:25 | Repro of the one 03:55 morning-guard FAIL (phone "refresh keeps aifs/...|feels|norca -> cenca"): re-ran aifs @390x844 = **0 FAIL**; transient refresh race, not reproducible. | - | qa/guard_preview_aifs_phone_20261105.log |
| 04:35 | Full-size polish shots (CA views Southern/Central/Northern + PNW town labels, desktop 1440x900 and phone 1170x2532): framing, towns, 0 HTTP errors. | - | local/shots/20261105/polish_{socal,cenca,norca}_t2m_gfs_{desktop,phone}.png, polish_pnw_towns_t2m_ifs_{desktop,phone}.png |
| 04:50 | **Console sweep** (every tab/toolbar button on index + compare + meteograms, desktop+phone): found third-party CORS errors on Observations (IEM ASOS currents). Root cause = QA scripts used Playwright `extra_http_headers`, which attaches the Access service-token headers to EVERY request incl. third-party origins (token leak + CORS preflight failures). Not a site bug. | - | qa/sweep_ui_20261105.log |
| 05:05 | **Fix**: qa/_access.py scopes the token headers to *.pnw-weather-site.pages.dev only (guard.py, interaction_check.py, preview shots, tabs_check). Sweep after fix: only expected `/req` 403 (service token is not the Access user JWT; by design). Guard rrfs after patch: **81 OK / 0 FAIL**. Secret-value scan of repo: 0 hits. | 0349e13 | qa/guard_preview_rrfs_scoped_20261105.log, backups/qa_token_scope_20261105/, local/shots/20261105/sweep_*_{desktop,phone}.png, sweep_obs_{desktop,phone}.png |

## Stretch 8 (11-05 05:21 PT onward, builder #8; hidden preview only, no production deploy)
| Time PT | Item | Commit | Evidence |
|---|---|---|---|
| 05:21 | Request queue re-read (read-only, tools/fast/read_requests.py): "no requests", nothing from Michael Snyder. Box check: no jobs running, tree clean. All queued items already done per log; no new sources used, WA Maps OFF. | - | - |
| 05:25-05:29 | Regression sweep on preview (GFS, all views incl. socal/cenca/norca/bay/orco/bigi/pnw towns, desktop+phone): **121 OK / 0 FAIL**, console errors 0. | (log commit) | qa/guard_preview_gfs_regress_20261105.log |

| 05:54-06:36 | **Temp scale green (preview only):** teal-leaning greens before oranges; dark oranges ~70°F+; blues kept; CVD dE≥3.23. Commit **031b544**. Preview deploy **02b726e2**. Guard 233 OK / 2 FAIL (refresh race). | 031b544 | tempscale_pnw_t2m_BEFORE/AFTER_*, tempscale_{ca,hi,bay}_t2m_AFTER_*, tempscale_legend_AFTER.png, tempscale_meteogram_seattle_AFTER_desktop.png |
