# Preview note: AIFS ENS and NOAA WaveWatch III on the hidden preview, 11-04 ~9:50 PM PT
- `aens` (ECMWF AIFS ENS, 50 members, CC BY 4.0): run 12Z 11-04, F6-F48. Products: ensemble mean t2m / anomalies / MSLP+precip / snowfall, chance of freezing, ensemble lows (member dots), spread, spaghetti. Ensemble lows panel and dots use the site theme colors. Normals reuse the IFS slots (grid_from).
- `gfsw` (NOAA GFS-Wave / WaveWatch III 0.25°, public domain, NOAA AWS open data): run 12Z 11-04, F3-F48. Products: significant wave height, swell period, wave height + swell period. Views na, pac, pnw, pnwt, ca, socal, cenca, norca, hiw. Change: `gfsw` added to regions.json `model_views` (it had no entry, so static crashed on the Washington views).
- Backups: backups/gfsw_20261104/ (regions.json, manifest before). qa/guard.py got an optional GUARD_MODELS filter (default = all models).
- Local QA guard (aens + gfsw): local/guard_local_aens_gfsw.log.
- Screenshots (full size, local/shots/20261104/, desktop 1440x900 + phone 390x844 @3x): aens_mslpqpf_pnw, aens_elows_pnw, aens_z500anom_na, aens_ep32_ca, gfsw_waves_pac, gfsw_swper_pnw, gfsw_swellhs_ca, gfsw_waves_hiw.
- Production untouched, nothing pushed to main.
