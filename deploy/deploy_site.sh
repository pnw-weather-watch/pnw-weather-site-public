#!/bin/bash
# ONE deploy script for the second site (pattern of the main site's guarded deploy; own code). NEVER run by the agent for production.
#   bash deploy/deploy_site.sh                 -> preview only: build, deploy branch "preview", read the preview URL, run qa/guard.py on it
#   bash deploy/deploy_site.sh --confirm       -> the above, then (only if the preview guard passed) production: record the previous
#                                                 production deployment, write ROLLBACK_prod_<id8>_<YYYYMMDD>.md, deploy branch main,
#                                                 run qa/guard.py on production and AUTO-ROLL BACK to the previous deployment if it fails.
# --confirm only after Benjamin's explicit "Push" then "Deploy". Fast-forward only: HEAD must equal origin/main and origin/main must be
# an ancestor of nothing local (no unpushed/diverged commits). Env (names only): PNW_CLOUDFLARE_API_TOKEN (the account is pinned and checked), optional
# QA_ACCESS_CLIENT_ID / QA_ACCESS_CLIENT_SECRET (Access service token so the guard can pass Access).
set -euo pipefail; cd "$(dirname "$0")"; K=$(cd .. && pwd)
PROJECT=pnw-weather-site; CONFIRM=0; [ "${1:-}" = "--confirm" ] && CONFIRM=1
: "${PNW_CLOUDFLARE_API_TOKEN:?PNW token (new account) required}"
# 11-04 safety: never use the shared CF_PAGES_KEY / CLOUDFLARE_ACCOUNT_ID (they belong to the OTHER site's account).
CF_PAGES_KEY="$PNW_CLOUDFLARE_API_TOKEN"; CLOUDFLARE_ACCOUNT_ID=b6dc205037fd8e8c37d5267ee61dc302
ACCTS=$(curl -s -H "Authorization: Bearer $CF_PAGES_KEY" https://api.cloudflare.com/client/v4/accounts | python3 -c "import json,sys;print(','.join(a['id'] for a in json.load(sys.stdin)['result']))")
[ "$ACCTS" = "$CLOUDFLARE_ACCOUNT_ID" ] || { echo "token does not see exactly the PNW account - refusing"; exit 1; }
API="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/$PROJECT"; AH="Authorization: Bearer $CF_PAGES_KEY"
git -C "$K" fetch -q origin
[ -z "$(git -C "$K" status --porcelain -- tools web deploy qa)" ] || { echo "working tree dirty: commit first"; exit 1; }
H=$(git -C "$K" rev-parse HEAD); O=$(git -C "$K" rev-parse origin/main)
[ "$H" = "$O" ] || { echo "HEAD $H != origin/main $O (fast-forward only: push first, never force)"; exit 1; }
bash build.sh >/dev/null; rm -rf functions && cp -r ../tools/fast/functions functions
LOG=$(mktemp); CLOUDFLARE_API_TOKEN="$CF_PAGES_KEY" npx wrangler pages deploy public --project-name=$PROJECT --branch=preview --commit-hash=$H --commit-dirty=true | tee "$LOG"
PV=$(grep -oE 'https://[a-z0-9-]+\.'$PROJECT'\.pages\.dev' "$LOG" | tail -1); [ -n "$PV" ] || { echo "no preview URL"; exit 1; }
echo "preview: $PV (Access-gated)"
python3 "$K/qa/guard.py" "$PV" 1440x900 390x844 > "$K/qa/guard_preview.log" 2>&1 || { echo "GUARD FAILED ON PREVIEW - not deploying"; grep -E '^FAIL' "$K/qa/guard_preview.log" | head; exit 2; }
echo "preview guard OK"
[ $CONFIRM = 1 ] || { echo "stop: preview only (production needs --confirm after Benjamin's Push + Deploy)"; exit 0; }
PREV=$(curl -s -H "$AH" "$API" | python3 -c "import json,sys;d=(json.load(sys.stdin)['result'].get('canonical_deployment') or {});print(d.get('id',''))")
D=$(date +%Y%m%d); RB="$K/ROLLBACK_prod_${PREV:0:8}_$D.md"
printf '# Rollback record %s\n- previous production deployment: %s\n- new commit: %s\n- preview tested: %s\n- rollback: POST %s/deployments/%s/rollback (Bearer CF_PAGES_KEY), or Pages dashboard > Deployments > Rollback\n' "$(date)" "${PREV:-none (first deploy)}" "$H" "$PV" "$API" "$PREV" > "$RB"; echo "wrote $RB"
CLOUDFLARE_API_TOKEN="$CF_PAGES_KEY" npx wrangler pages deploy public --project-name=$PROJECT --branch=main --commit-hash=$H
if ! python3 "$K/qa/guard.py" "https://$PROJECT.pages.dev" 1440x900 390x844 > "$K/qa/guard_prod.log" 2>&1; then
  echo "GUARD FAILED ON PRODUCTION"; grep -E '^FAIL' "$K/qa/guard_prod.log" | head
  if [ -n "$PREV" ]; then curl -s -X POST -H "$AH" "$API/deployments/$PREV/rollback" | python3 -c "import json,sys;r=json.load(sys.stdin);print('rolled back to previous:',r.get('success'))"; echo "- AUTO-ROLLED BACK $(date) (guard failed)" >> "$RB"
  else echo "first deploy, nothing to roll back to: delete the deployment in the dashboard"; fi; exit 3; fi
echo "production guard OK"; echo "- production guard OK $(date)" >> "$RB"
