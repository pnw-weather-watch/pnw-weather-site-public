# PREVIEW / PROD promote — temp scale all models — 2026-11-05

- **Scale commit:** `cb7899e` (+ theme under/over wiring).
- **Request (Benjamin 8:16 AM PT):** Push and deploy; color scheme on all models' temperature maps.
- **Wiring:** All t2m / d2m / feels / nmaxt / nmint / ehigh / elow products use `HS.temp_cmap()` ← `theme/temp_scale.json` via `theme.apply_house_style`. Anomaly maps keep `anom_scale.json`. Meteograms read the manifest t2m table.
- **Fix:** `TEMP_UNDER` / `TEMP_OVER` now taken from `temp_scale.json` (was leftover house_style white/pink).
- **Data:** Regenerated temp keys for gfs, ifs, hrrr, rrfs, nbm, aifs, eps, aens; sample hours re-encoded; synced `preview/` then promoted to live (no overwrite of existing live packs except run.json + manifest).
- **Production:** deploy via `deploy/deploy_site.sh --confirm` after preview QA.

- **CA views (8:33 AM):** Central + Southern California E–W width matched to Northern California (centers kept). See `backups/ca_width_match_20261105/`.
