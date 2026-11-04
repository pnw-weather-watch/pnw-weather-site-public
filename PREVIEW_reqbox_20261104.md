# PREVIEW reqbox 2026-11-04 (local hidden preview only, nothing deployed)
- Added "Request a change" pencil button (menu bar on viewer; bottom corner on compare/meteograms, which have no #bar), copied from Benjamin's site with Studio/Social pin logic removed and colors from theme.css.
- /req Pages Function (tools/fast/functions/req.js): Access team is a placeholder/`ACCESS_TEAM` env var (second site's own team), DATA = new bucket only. read_requests.py uses R2_BUCKET env.
- Mocked with local/req_stub_server.py (in-memory /req). Send -> "Sent, queued", list shows newest; hidden with ?clean=1. 0 console errors on viewer/compare.
- Shots: local/shots/reqbox/reqbox_open_{desktop,phone}.png, reqbox_{compare,meteograms}_{desktop,phone}.png
- Not created: Pages project, R2 bucket, Access app. See tools/fast/REQUEST_BOX.md (Access required; Turnstile + rate limit if public).
