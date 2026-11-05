# Morning report — second site overnight (Thu 11-05 PT)

**Scope:** Access-gated preview only (`preview.pnw-weather-site.pages.dev`). No production deploy. WA Maps never. No Studio/Social. WW3 listed as open decision only.

## Done (Benjamin 12:16 AM + Weather Bot B)

| Item | Status | Evidence |
|---|---|---|
| Hawaii waves = ECMWF IFS open wave (no PacIOOS) | Done | `f5ef608`, `80ef26c`; `waves_hiw_ifs_AFTER_fix_*` |
| Extra views Bay Area / Oregon coast / Big Island | Done | `bay`/`orco`/`bigi` on preview; gust3 + waves shots |
| Ensembles longer (EPS mean, epsm, AENS) | Done **through F360** | EPS 84, epsm 40, AENS 60 steps; `*_ext_f360_AFTER_*` |
| PNW town labels on t2m + MSLP anomaly | Done | `pnw_*_AFTER_towns_*` |
| Pass/meteogram snow floors (≥12 in/6h, ≥3 in/h rate) | Done | `c6077eb`, `a9aae70`; winter meteogram shot |
| ECMWF 3h / 6h max gust maps | Done | `gust3_AFTER_*`, `gust6_AFTER_*` |
| Sat viewer 4h loop + scrubber row ~5 in | Done | `obs_sat_loop4_AFTER4_desktop.png` (slideW=480) |
| F+ badge placement | Verified | `badge_F_check_*`, F+360 on EPS |
| Ensemble-low color key | Verified | `elows_key_check_*` |
| Buoys / towns / H/L carried over | Verified | `buoys_hl_waves_pnw_*`, HI wave VERIFY |
| viewStatic console errors on HI/EPS | Fixed | `e21f691`, `ace1f05` |

## QA

- Ensemble F360 guard: **FINAL_OK 277 / 0 FAIL** (`qa/guard_preview_ens_f360_20261105.log`)
- Earlier Stretch4 / B guards: 848 OK, 414 OK (see overnight log)

## Open for Benjamin

See `SUMMARY_overnight_20261104.md` — especially WW3/`gfsw` disposition, Push+Deploy when ready, PacIOOS never, WA Maps never.

## Meteogram colors

Yes — `70cf9da` / `8287d31` earlier overnight (site temp palette on lines/boxes).

## Weather Bot ask (parent: DraftExternalMessage)

Draft staged at bot store `drafts/weather_bot_status_20261105.md`.

## Late QA (04:18-05:10 PT, builder #7)
- Request queue: empty (nothing from Michael Snyder). No new work items.
- UI console sweep (all tabs/buttons, desktop + phone): clean. Only `/req` 403 with the QA service token (expected: `/req` requires the real Access user).
- **Security note:** until 0349e13 the QA scripts sent the Access service-token (`pnw-qa`) headers to every origin the page called (e.g. mesonet.agron.iastate.edu on the Observations tab). Fixed (headers now scoped to the Pages host). Recommend rotating the `pnw-qa` token in the new Cloudflare Access when convenient (values never logged in the repo; 0 hits).
- The one 03:55 morning-guard failure (phone refresh norca->cenca) did not reproduce (aifs re-run 0 FAIL).
- Data freshness: preview model runs are the Nov 4 cycles (GFS 18Z, ECMWF/AIFS 12Z, EPS 00Z, HRRR/RRFS/NBM 00Z Nov 5); no cycle refresh was run overnight (publishing a fresh cycle is a live-data step to decide).
