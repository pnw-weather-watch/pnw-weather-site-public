# Manifest: second site code kit (11-3-26, Pacific time)

The kit was built from the newest origin/main of Benjamin's site repo (commit bf6fff2, his production at build time). This is a copy only. Benjamin's repo, deploys, R2, Pages project and workflows were not modified.

## Stripped (removed, not just hidden)
- **Studio:**
  - Files not copied: studio.html, studio.js, tools/fast/studio_views.py.
  - Removed from viewer.js: the Studio tab button and handler, `?studio=` handling (wantRS sharp mode, STUDIO_DRAG_RS, the drag lite override), addStudioViews() / the "Washington (wide, for loops)" view, the studio_views.json fetch and the PV.studio supplement, the `V.studioOnly` key/credit checks, the onStudioDraw/onStudioSkip/studioLabelHidden hooks, Studio-only comments, and Q.get("studio") on the low panel.
  - Removed from compare: the TV 16:9 button, its handler and its CSS. The caption "for TV / YouTube" became "Main map".
  - fast_encode.py no longer calls studio_views.build. The non-Studio Pacific NW tight town fix it also called (`pnwt_fix` + `town_slots`) was moved to tools/fast/view_fixes.py.
  - The mp4-muxer vendor folder (Studio MP4 export only) and its credit text were removed.
- **Social:** social.html, social.js, socialloop.js, tools/fast/social/, publish_products_x.py, the Social tab button and handler.
- **Alerts:** alert_relay/, alert-relay.yml, and all Buffer, Slack and posting scripts (none were copied). alert_style.md is not included.
- **Request a change box:** reqbox.js, its script tag, functions/req.js, read_requests.py.
- **WA Maps tab:** the button and handler, wamaps.html/js, wamaps/, tools/fast/wamaps/, stormfind.js (Studio/Social storm finder).
- **Old-site workflows:** forecast-deploy.yml, forecast-poll.yml, forecast-site.yml.
- **Benjamin's look assets:** brand/ logos, Montserrat and the old-site fonts, mkeys/ and slayers/ (his rendered keys and town layers).
- **WA-only views** (removed in regions.json and regions.py): wa, wwa, ewa, puget, bc, lm, newa, wawide. Kept: na, pnw, pnwt, pnwhr, passes. Added: pac, ca, capasses, hiw.

## Changed for the theme and regions (marked `[THEME]`, `[KIT]` in the code)
- Site: theme.css (CSS variables + the WXTheme font). index, compare and meteograms CSS colors became `var(--...)`. Canvas chrome colors come from `TH`, and the H/L colors from `--map-hi/--map-lo`. The `pdata` preview supplement loads only with `?pv=1`.
- Python: theme.py (applied at the end of house_style.py and in menu_maps.py), regions.py (called from fast_encode.extra_views), and a Sierra Passes branch in fast_encode town_call.
- The viewer's default view, H/L and ensemble-low tuning for the new views come from regions.json (tools/apply_regions_site.py).
- web/forecast/base.css and forecast.css use the theme font (the old-site font-faces were removed).

## Redacted (placeholders)
- Cloudflare account id → `<ACCOUNT_ID>`
- Pages project name → `<PAGES_PROJECT>`
- GitHub owner → `<GITHUB_OWNER>`
- R2 bucket → `<R2_BUCKET>`
- Access team host → `<ACCESS_TEAM>`
- Secret names are kept (CF_PAGES_KEY, CLOUDFLARE_ACCOUNT_ID), never values. Preview hostnames in the notes now read `<hash>.<PAGES_PROJECT>.pages.dev`.

## Included from Michael's design folder (theme/michael_design)
THEME_PROPOSAL, PRODUCT_LOOKS_PLAN, STYLE_RULES_DRAFT, CREDITS_LEGAL, LEGAL_RULES, design_brief and ca_pass_view_notes (all .md); anom_scale.json (v6), snow_scale_v6.json/.py, temp850_scale.py, theme_coastal_daylight.py, theme_cd_waves_v4.py; ca_passes.csv, ca_airports.csv, pnw_airports.csv; the Atkinson Hyperlegible fonts (OFL).

## Not included (ask if needed)
deploy_*.sh with real ids, .wrangler/, node_modules, box_tools (the QA sweep and r2proxy scripts), data/ and logs, and the archive/ folder.
