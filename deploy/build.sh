#!/bin/bash
# Build the static site into deploy/public (no Studio, Social or WA Maps; request box = reqbox.js + functions/req.js). Data comes from R2 via functions/d.
set -e; cd "$(dirname "$0")"; K=..; SRC=$K/tools/fast/site
rm -rf public; mkdir -p public/fonts public/obs public/old
cp $K/web/forecast/obs/obs.js $K/web/forecast/obs/obs.css $K/web/forecast/obs/basemap.json $K/web/forecast/obs/obsimg.js public/obs/
cp $SRC/fonts/* public/fonts/; cp $SRC/theme.css $SRC/selection.js $SRC/viewer.js $SRC/cameras.js $SRC/coastline.js $SRC/compare.html $SRC/compare.js $SRC/meteograms.js $SRC/buoys_ndbc.json $SRC/reqbox.js public/
if [ -d $SRC/cam ]; then cp -r $SRC/cam public/cam; fi
cp $K/web/forecast/base.css $K/web/forecast/forecast.css public/old/
for d in mkeys slayers; do [ -d $SRC/$d ] && cp -r $SRC/$d public/ || true; done   # site-shipped "@" keys / town layers once you generate them
inj='s#<head>#<head><meta name="robots" content="noindex,nofollow">#'
sed -e 's#<script src="viewer.js#<script>window.WX_DATA="/d/"</script><script src="viewer.js#' -e "$inj" $SRC/index.html > public/index.html
sed -e 's#<script src="meteograms.js"></script>#<script>window.WX_DATA="/d/"</script><script src="meteograms.js"></script>#' -e "$inj" $SRC/meteograms.html > public/meteograms.html
# The query on viewer.js used to be a hand-written date, so a new deploy kept
# requesting viewer.js?v=20261106canvas. Stamp every local JS/CSS URL with this commit.
SHA=$(git -C "$K" rev-parse --short=12 HEAD 2>/dev/null || echo dev)
python3 - "$SHA" << 'PY'
import pathlib, re, sys
sha = sys.argv[1]
root = pathlib.Path("public")
for p in list(root.glob("*.html")) + list(root.glob("*.js")):
    t = p.read_text()
    t2 = re.sub(r'((?:src|href)="(?:theme\.css|viewer\.js|selection\.js|coastline\.js|cameras\.js|meteograms\.js|compare\.js|reqbox\.js))(?:\?v=[^"]*)?"',
                rf'\1?v={sha}"', t)
    t2 = t2.replace('v: "20261107warp"', f'v: "{sha}"')
    if t2 != t:
        p.write_text(t2)
print("asset query", sha)
PY
mkdir -p public/functions 2>/dev/null; rm -rf public/functions
printf '/*\n  X-Robots-Tag: noindex\n/viewer.js\n  Cache-Control: no-cache, must-revalidate\n/cameras.js\n  Cache-Control: no-cache, must-revalidate\n/selection.js\n  Cache-Control: no-cache, must-revalidate\n/coastline.js\n  Cache-Control: no-cache, must-revalidate\n/theme.css\n  Cache-Control: no-cache, must-revalidate\n/index.html\n  Cache-Control: no-cache, must-revalidate\n/meteograms*\n  Cache-Control: no-cache, must-revalidate\n/compare.*\n  Cache-Control: no-cache, must-revalidate\n/reqbox.js\n  Cache-Control: no-cache, must-revalidate\n/cam/*\n  Cache-Control: public, max-age=31536000, immutable\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n' > public/_headers
printf '{"version":1,"include":["/d/*","/req"],"exclude":[]}\n' > public/_routes.json
echo "built deploy/public (functions: copy ../tools/fast/functions next to public when deploying: wrangler reads ./functions)"
