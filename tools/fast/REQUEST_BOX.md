# "Request a change" box (second site)
- Front end: `tools/fast/site/reqbox.js` (pencil button in the top menu bar, before the status; bottom-left if a page has no bar). Max 2000 chars, Send, newest 10 requests. Hidden with `?embed`, `?clean=1`, `?make` and `body.rec`.
- Back end: `tools/fast/functions/req.js` (Pages Function `/req`). It verifies the Cloudflare Access JWT against `ACCESS_TEAM` (Pages env var; the placeholder refuses everything) and stores `requests/<ISO time>_<id>.json` in R2 bound as `DATA`, using the second site's NEW bucket only.
- Reader: `R2_BUCKET=... python3 tools/fast/read_requests.py [--json] [--mark KEY done]`, with credentials from the env only.
- **Security:** the site must sit behind its own Cloudflare Access policy (the second site's own team, never the first site's). If the site is ever made public, add Turnstile and a rate limit to `/req` first.
- Not created yet: the Pages project, the R2 bucket and the Access app.
