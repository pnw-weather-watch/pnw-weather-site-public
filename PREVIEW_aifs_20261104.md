# Preview note: AIFS (ECMWF AIFS single, 0.25°) on the hidden preview, 11-04 ~9:45 PM PT
- Model `aifs`: run 12Z 11-04, F6-F48 (6-hourly), all views (na, pac, pnw, pnwt, ca, socal, cenca, norca, hiw), 44 products. Data: ECMWF open data, CC BY 4.0 (credit line on the map and in the footer).
- Change: `grid_from="ifs"` for aifs in fast_encode.py (reuses the IFS normals slots so the anomaly products render; no new data source).
- Backup: backups/aifs_20261104/ (fast_encode.py, regions, manifest before/after static).
- Local QA guard (qa/guard.py, 1440x900 + 390x844): aifs t2m + feels on every view OK, 0 console errors (local/guard_local_aifs.log).
- Screenshots (full size, local/shots/20261104/): aifs_t2m_pnw, aifs_mslp_pac, aifs_z500a_na, aifs_qpf_ca (each _desktop.png 1440x900 and _phone.png 390x844 @3x).
- R2: local data only until the next preview sync (preview/ prefix). Production untouched, nothing pushed to main.
