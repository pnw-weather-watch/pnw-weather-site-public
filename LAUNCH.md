# Launch guide: second site (Pacific NW, California, Hawaii)

The kit was built on 11-3-26 (Pacific time) from the newest main of Benjamin's site (commit bf6fff2, his production at the time). The layout is the same as his site, without Studio, Social, alerts, the "Request a change" box or the WA Maps tab. All palettes, fonts and colors come from the theme layer, which is set to your "Coastal Daylight" theme.

## Ground rules (Benjamin's)
1. **Hidden preview first.** Build and deploy only to a preview branch. Production waits until Benjamin says **Push**, and then **Deploy**.
2. Push is fast-forward only. Never force-push.
3. Before each production deploy, write `ROLLBACK_prod_<id>_<date>.md` with the previous production deployment id. Run QA right after. If QA fails, roll back at once.
4. No secrets, account ids, tokens or Access details in files, chat or commits. Use repo secrets and environment variables only.
5. Data: public domain, or a free license that allows public use with credit, and show the credit. ECMWF open data is CC BY 4.0 and needs a credit line. Read `theme/michael_design/LEGAL_RULES.md` and `CREDITS_LEGAL.md`.

## What is Benjamin's look vs. neutral code
- **Neutral code (keep as is):** all drawing, placement, collision, zoom, save, compare, meteogram, observation and ensemble logic in `tools/fast/site/*.js`, `web/forecast/obs/*.js`, `tools/fast/*.py` and `tools/forecast/*.py`.
- **Theme (yours):** `tools/fast/site/theme.css` sets the page chrome colors, the font (Atkinson Hyperlegible, OFL) and the H/L colors. `theme/theme.json` sets the map tokens. `tools/forecast/theme.py` replaces Benjamin's `house_style` palettes, font, key label size, the H/L colors and the snow scale (it runs at the end of `house_style.py` and in `menu_maps.py`). The scale JSONs (`theme/temp_scale.json`, `theme/qpf_wave_scales.json`, `theme/michael_design/anom_scale.json`, `snow_scale_v6.json`) come from your design folder.
- **Benjamin's values still in the code:** these are fallbacks that the theme overrides, plus a few hard-coded colors listed under Known gaps (ensemble dot colors, some wave label colors). Don't ship his exact ramps. A preview is at `theme/theme_scales_preview.png`.

## Launch order
1. **Repo:** create your own repo and copy the kit into it, keeping the tree as is. Add the secrets `CF_PAGES_KEY` (a Cloudflare token with Pages and R2 edit) and `CLOUDFLARE_ACCOUNT_ID`. Never paste the values anywhere else.
2. **Storage and Pages:** create your own R2 bucket and Pages project. Then replace the placeholders:
   - `<R2_BUCKET>` in `.github/workflows/fast-models.yml`, `tools/fast/upload_r2.py` (or set the `R2_BUCKET` env var) and the comments.
   - `<PAGES_PROJECT>` (or set the `PAGES_PROJECT` env var for `deploy/*.sh`).
   - `<GITHUB_OWNER>`.
   - Bind the bucket to the Pages project as `DATA`. `tools/fast/functions/d/[[path]].js` serves `/d/<key>`.
   - Put the site behind your own Cloudflare Access app.
3. **Python environment:** run `pip install -r tools/requirements.txt`. On some boxes the cartopy import aborts at interpreter exit ("free(): invalid pointer"). Benjamin's original code does the same. It's harmless, but end scripts with `os._exit(0)` if it trips CI.
4. **Regions:** check `regions/regions.json`. It holds the views (na, pac, pnw, pnwt, pnwhr, passes, ca, capasses, hiw), the per-model view lists, town tiers, H/L rules, barb density, the CA passes (your `ca_passes.csv` v3, plus Black Butte Summit) and the California Passes towns. `tools/forecast/regions.py` loads it, and `fast_encode.extra_views()` calls it. Frame previews of the new views are in `qa/regions/`.
5. **Static layers first:** for each model, run `python tools/fast/fast_encode.py` in static mode (see `tools/fast/README.md` and `fast_encode.static()`). This builds the LUTs, basemaps, town layers, keys and `manifest.json` in your theme. Then run `python tools/fast/view_fixes.py --manifest <out>/manifest.json --out <out>` and `tools/fast/wave_views.py`. Upload with `upload_r2.py`.
6. **One model cycle:** run `tools/fast/fast_cycle.py` for GFS, then upload. Check that `manifest.json` lists the new views.
7. **Workflow:** enable `.github/workflows/fast-models.yml` only after step 6 works by hand. Start with GFS and HRRR, then add models. ECMWF needs its CC BY credit.
8. **Hidden preview:** run `PAGES_PROJECT=... bash deploy/deploy_preview.sh`. It builds `deploy/public` and deploys to the `preview` branch.
9. **Verify** (see below), then show Benjamin the preview link and screenshots.
10. **Production**, only after he says Push and then Deploy: run `C=<sha> bash deploy/deploy_prod.sh`, write the rollback note, and run QA.

## Verify on the preview (desktop and phone)
- Run `python3 qa/viewer_smoke.py <preview-url>/` and `python3 qa/obs_smoke.py <url>/`. You need zero console errors and zero HTTP errors. The tabs should be Surface, Precip, Snow, Upper Air, Severe, (Waves), Compare, with no Studio, Social or WA Maps.
- Go through `DETAILS_CHECKLIST.md` line by line on at least one product per family.
- Check each new view (pac, ca, capasses, hiw): town placement, pass labels, the H/L markers away from the edges, and keys that are not crowded.
- Credits match `LEGAL_RULES.md` on every product.

## Rollback
To roll back, run `POST /accounts/<ACCOUNT_ID>/pages/projects/<PAGES_PROJECT>/deployments/<previous_id>/rollback` with your token, or use Rollback in the Pages dashboard. Keep one `ROLLBACK_prod_*.md` per deploy with the previous id, the commit and the exact command.

## Rebuilding the stripped site from a newer copy of Benjamin's code (only if he asks)
`tools/strip_studio.py <site>` → `tools/apply_theme_site.py <site>` → `tools/apply_regions_site.py <site> regions/regions.json`. Each script stops with "MISSING ..." if the source changed, so nothing is half-applied. Then copy `theme.css` and `fonts/` in.

## File map
- `tools/fast/site/`: index.html (viewer), viewer.js, compare.html/js, meteograms.html/js, theme.css, fonts/ (Atkinson), buoys_ndbc.json
- `web/forecast/obs/`: observations map (obs.js, obsimg.js for radar and satellite, basemap.json), plus `web/forecast/base.css` and `forecast.css` (meteogram page styles)
- `tools/fast/`: encoder and cycles (fast_encode.py, fast_cycle.py, epsm/aensm cycles, members, oisst, wave_views.py, view_fixes.py, upload_r2.py, backfills), functions/d (the R2 reader)
- `tools/forecast/`: renderers (house_style.py + **theme.py**, **regions.py**, temp_maps, menu_maps, ens_maps, member_grid, meteograms, meteo_suite, clim builders, ...)
- `theme/`: theme.json, scale JSONs, scale preview, michael_design/ (your design docs and scale sources)
- `regions/regions.json`
- `deploy/`: build.sh, deploy_preview.sh, deploy_prod.sh
- `.github/workflows/fast-models.yml` (template)
- `reference/benjamin_notes/`: STYLE_RULES.md, OBS_STYLE.md, SATELLITE_TERMS_FINAL.md, previews/ (per-feature decisions)
- `qa/`: smoke tests, screenshots (viewer/), region frames (regions/)
- `DETAILS_CHECKLIST.md`, `MANIFEST.md`, `SCAN.txt`

## Known gaps (to finish on the preview)
1. **Site-shipped keys and town layers** (`mkeys/`, `slayers/`, "@" paths) aren't included because they're Benjamin's look. Regenerate them in your theme. The MSLP anomaly key `key_<m>_mslpa_a80_<view>.png` and the 18 in QPF key `key_<m>_<pid>_q18_<view>.png` are referenced in viewer.js around line 357.
2. **Meteogram towns** (`tools/forecast/meteograms.py TOWNS` and the encoder town points) are still Benjamin's WA list. Replace them with PNW, CA and HI stations.
3. **Observation presets** are PNW only (obs.js). Add California and Hawaii.
4. **Wave map coast towns and offshore points** (viewer.js `COAST_TOWNS/COAST_VIEWS/WAVE_*`) are Washington-specific. The CA and HI buoys are already in `BUOYS`. Add CA/HI coast entries, or let those views use `OWN_DEFAULT`.
5. **Your wave scales and snow change scale** are in the theme layer but aren't yet wired into the encoder's wave and `dsnod` tables (fast_encode around lines 1009-1180).
6. **Kit additions to confirm with you:** 2 m temperature above 80°F (wine to orchid), precip above 3 in (gold to umber), the Sierra-view town list, and the new view frames and H/L tuning for pac, ca and hiw.
7. **Hard-coded colors that are still Benjamin's:** ensemble member dot colors (viewer.js `DOT_COLS`, ens_maps.py), some label and halo colors in viewer.js, and the anomaly/MSLP anomaly palette helpers in fast_encode around lines 955-960. Recolor them in the theme.
8. **Header and corner-tag layout is unchanged** (same layout, as Benjamin asked). Your THEME_PROPOSAL describes a time tile and a vertical key. Those would change the layout, so they aren't applied. Ask Benjamin before changing them.
9. The smoke test ran against an old local HRRR sample only (Washington and Pacific NW high-res views). Waves, ensembles, member lookup and new-region rendering still need checking on real data on your preview.
10. The workflow still lists `aensm`, `epsm` and `oisst` jobs. Keep or drop them as you choose.

## Wired config (2026-11-04)
- Cloudflare account: new account (id via `GET /accounts`), Pages project `pnw-weather-site` (production branch `main`, not deployed), R2 bucket `pnw-models-data`.
- Pages binding `DATA` -> R2 `pnw-models-data` set via API on preview AND production configs. Env vars `ACCESS_TEAM=https://broad-king-ded7.cloudflareaccess.com`, `ACCESS_AUD=<aud of Access app 63a0dd46-14e2-44b3-a529-f5decd294522>` (req.js now checks iss + aud + exp + signature).
- Access apps: pnw-weather-site.pages.dev and *.pnw-weather-site.pages.dev, owner@example.com only.
- GitHub repo secrets NOT set (names only): CF_PAGES_KEY, CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY. Workflow schedule stays disabled.
