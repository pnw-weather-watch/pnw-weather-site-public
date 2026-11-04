# Safety measures for the second site (pnw-weather-site)

Adapted from the main site's guarded workflow (pattern only, no files or secrets copied).

## Deploy
- `deploy/deploy_site.sh` is the only deploy path. It is fast-forward only (HEAD must equal origin/main and the tree must be clean; never force-push). It deploys preview first (branch `preview`), reads the preview URL and runs `qa/guard.py` on it.
- Production needs `--confirm`, which is used only after Benjamin says "Push" and then "Deploy". The agent never runs it with `--confirm`.
- Before production, the script writes `ROLLBACK_prod_<previous-id8>_<YYYYMMDD>.md` with the previous deployment and the rollback command. After deploying it runs the guard on production and **automatically rolls back** to the previous deployment if any check fails.

## Automated tests that block a deploy (`qa/guard.py`, exit 1 = blocked)
- Page refresh reopens the same run, product and view, for every view × the first 2 products of every model.
- Layout: the map stays inside the viewport and there is no horizontal overflow (desktop 1440x900, phone 390x844).
- Console errors, page errors and HTTP ≥400 responses must all be 0.
- The data proxy answers (`/d/manifest.json` returns 200 JSON).
- The newest model run is listed first and loaded by default.
- Colorblind check: under deutan/protan simulation, adjacent samples along each product key must keep ΔE ≥ 3.
- Behind Access the guard needs an Access service token in env `QA_ACCESS_CLIENT_ID` / `QA_ACCESS_CLIENT_SECRET` (names only here).

## Secrets
- No secret values live in the repo. The token goes in a one-shot `http.extraheader` at push time and is never stored in `.git/config`.
- Full-history scan on 2026-11-04 (all refs, 14 commits): 0 token, key or private-key patterns, and 0 matches of the live secret values. One 64-hex hit is the Access app AUD, which is a public identifier present in every Access JWT and not a secret.
- Repo secret names for CI (not set yet): CF_PAGES_KEY, CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY.

## Request box (spam / abuse)
- The whole host is behind Cloudflare Access (owner@example.com only). `/req` also verifies the Access JWT itself (signature, issuer `broad-king-ded7`, AUD, expiry).
- POST requires the custom header `X-WX-Req: 1` and JSON. The body is limited to 8000 bytes and the text is cut at 2000 characters.
- Each request is stored as one file in R2 (`requests/<time>_<id>.json`, new bucket only). Nothing is executed from it, and the agent reads the queue.

## Cost caps
- Benjamin must set a budget/usage alert in the NEW Cloudflare account: dashboard → Notifications → Add → "Usage Based Billing" (pick R2 storage/operations and Workers/Pages Functions requests, set a low threshold), and check Billing → Billable usage.
- Avoid unlimited public reads: there is no public r2.dev URL and no custom public bucket domain. Data is served only through the `/d/` function behind Access.
- Keep the whole site behind Access until go-live. The GitHub workflow schedule stays disabled (private-repo minutes).
