#!/bin/bash
# Build the static site into deploy/public (no Studio, Social, WA Maps or request box). Data comes from R2 via functions/d.
set -e; cd "$(dirname "$0")"; K=..; SRC=$K/tools/fast/site
rm -rf public; mkdir -p public/fonts public/obs public/old
cp $K/web/forecast/obs/obs.js $K/web/forecast/obs/obs.css $K/web/forecast/obs/basemap.json $K/web/forecast/obs/obsimg.js public/obs/
cp $SRC/fonts/* public/fonts/; cp $SRC/theme.css $SRC/viewer.js $SRC/compare.html $SRC/compare.js $SRC/meteograms.js $SRC/buoys_ndbc.json public/
cp $K/web/forecast/base.css $K/web/forecast/forecast.css public/old/
for d in mkeys slayers; do [ -d $SRC/$d ] && cp -r $SRC/$d public/ || true; done   # site-shipped "@" keys / town layers once you generate them
inj='s#<head>#<head><meta name="robots" content="noindex,nofollow">#'
sed -e 's#<script src="viewer.js#<script>window.WX_DATA="/d/"</script><script src="viewer.js#' -e "$inj" $SRC/index.html > public/index.html
sed -e 's#<script src="meteograms.js"></script>#<script>window.WX_DATA="/d/"</script><script src="meteograms.js"></script>#' -e "$inj" $SRC/meteograms.html > public/meteograms.html
mkdir -p public/functions 2>/dev/null; rm -rf public/functions
printf '/*\n  X-Robots-Tag: noindex\n/viewer.js\n  Cache-Control: no-cache\n/theme.css\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n/meteograms*\n  Cache-Control: no-cache\n/compare.*\n  Cache-Control: no-cache\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n' > public/_headers
printf '{"version":1,"include":["/d/*"],"exclude":[]}\n' > public/_routes.json
echo "built deploy/public (functions: copy ../tools/fast/functions next to public when deploying: wrangler reads ./functions)"
