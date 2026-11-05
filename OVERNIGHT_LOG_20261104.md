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

| 20:00 | Benjamin Push+Deploy: promote preview/ to live R2 (1387 new objects), production deploy of built products | (pending) | production screenshots |
