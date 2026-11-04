> SUPERSEDED by PREVIEW_wave_scale_85ft_20261101.md (11-01 ~7:55 AM)
# Max wave height scale 0-40 -> 0-60 ft: HIDDEN PREVIEW ONLY (11-01-2026 ~7:50 AM PST)
Benjamin 11-01 7:30 AM (t1974u): "adjust the max wave height scale to go up to at least 60'".
- Local commit d333803 on live_main checkout (branch main, ahead of origin/main c2a1e39 by 1). NOT pushed.
- Preview deploy d6d4ada3 (branch "fast"): https://d6d4ada3.<PAGES_PROJECT>.pages.dev  viewer.js?v=20261101c
- Production unchanged: canonical bb67543f (viewer.js?v=20261101b, still shows 0-40 with old keys).
What changed
- fast_encode.py: wavemax + wavemax24 get WVX_L = 0..40 (same bins/colors) + 45,50,55,60; anchors 47.5 #5a2a9e, 55 #9b7fe0, 60 #d2bff5,
  over 60 = #f3ebff; ticks 0,4,8,14,20,28,40,50,60. Significant Wave Height (waves) unchanged (CM["wavemax"] used to alias CM["waves"]; now split).
  New key file names via keyver "_60" (static/key_ifs_wavemax_60_<view>.png, ..._wavemax24_60_...), WX_KEY_PIDS env for a targeted key build.
- viewer.js: allProds also reads manifest models[m].products_p (over products/products_x). index.html + studio.html v=20261101c.
- R2 (shared data, invisible to production's viewer): 44 new key PNGs (11 views x 2 products, 1x + x2) and manifest models.ifs.products_p
  = {wavemax, wavemax24} (script /workspace/wave_scale_report/publish_products_p.py; manifest before: /workspace/wave_scale_report/manifest_before.json).
  Box copy fast_deploy/data/manifest.json merged too (before: /workspace/wave_scale_report/local_manifest_before.json).
  Map data needs no re-encode: fields are quantized with per-step lo/hi, values above 40 ft were never clipped.
To ship (only on his "Push"/"Deploy"): git push (fast-forward); deploy fast_deploy as usual (production viewer then reads products_p).
Undo preview state: git reset --hard c2a1e39 in live_main (local only), and remove products_p:
  manifest models.ifs.pop("products_p") via ETag write (production ignores it anyway). Extra key PNGs can stay.
Note: a full publish_static.py from an older box copy could drop products_p (preview would just fall back to 0-40).
