#!/bin/bash
# HIDDEN PREVIEW deploy (branch "preview"). Never production. Placeholders: fill from your own secrets store, never commit values.
set -e; cd "$(dirname "$0")"; : "${CF_PAGES_KEY:?}" "${CLOUDFLARE_ACCOUNT_ID:?}" "${PAGES_PROJECT:?}"
bash build.sh; rm -rf functions && cp -r ../tools/fast/functions functions
CLOUDFLARE_API_TOKEN="$CF_PAGES_KEY" npx wrangler pages deploy public --project-name="$PAGES_PROJECT" --branch=preview --commit-dirty=true
