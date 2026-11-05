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
| 21:35 | #12 member grids + #13 member meteograms (EPS mem data F3-F48 + epsm F6-F72); MSLP a80 keys for socal/cenca/norca into site mkeys; epsm model wired on preview | (pending) | mgrid_tmax_*, mlines_t2m_*, mgrid_qpf_*, meteograms_honolulu_*, mslpa_a80_*_desktop.png, epsm_mslp_m01_pnw_desktop.png |
