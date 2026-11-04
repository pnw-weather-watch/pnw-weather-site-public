#!/bin/bash
# PRODUCTION deploy. Only after Benjamin says "Push" (fast-forward main) and then "Deploy". C must equal origin/main.
set -e; cd "$(dirname "$0")"; : "${CF_PAGES_KEY:?}" "${CLOUDFLARE_ACCOUNT_ID:?}" "${PAGES_PROJECT:?}" "${C:?commit}"
git fetch -q origin; [ "$(git rev-parse origin/main)" = "$(git rev-parse $C)" ] || { echo "origin/main != $C"; exit 1; }
bash build.sh; rm -rf functions && cp -r ../tools/fast/functions functions
CLOUDFLARE_API_TOKEN="$CF_PAGES_KEY" npx wrangler pages deploy public --project-name="$PAGES_PROJECT" --branch=main --commit-hash=$(git rev-parse $C)
echo "Write ROLLBACK_prod_<id>_<date>.md with the previous production deployment id BEFORE QA."
