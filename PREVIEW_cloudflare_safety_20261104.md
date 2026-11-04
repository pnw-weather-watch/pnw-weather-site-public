# Preview notes 2026-11-04: Cloudflare wiring, fixes, safety, first hidden preview
- Config wired (bucket, project, owner, Access team + AUD). Pages binding DATA=pnw-models-data and env ACCESS_TEAM/ACCESS_AUD are set via API on the preview and production configs.
- Fixes: the GFS footer no longer credits ECMWF. Sierra Passes now show real numbers (they were stuck at "88").
- Fresh screenshots are in local/shots/fresh_20261104/ (desktop 1440x900, phone 390x844@3x).
- Local guard: 68 OK, 4 FAIL, all on the colorblind check for the t2m/feels key (deutan/protan min dE 1.2-1.3 between neighbours).
- R2: 2445 files from local/data (GFS 00Z 11-04, IFS) uploaded with tools/fast/sync_r2_s3.py.
- Hidden preview: https://preview.pnw-weather-site.pages.dev (deploy e41fc9f3). Every URL redirects to the Access login (302 to broad-king-ded7), and production has no deployment.
