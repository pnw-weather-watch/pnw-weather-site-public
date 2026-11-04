# AIFS ENS members (aensm) - hidden preview, PAUSED 11-03 6:12 AM PST (parent: video hook clips first)
Branch aens-members in live_main, commit c452218 (on main 0729b69). Nothing pushed or deployed; no R2 writes.
Code:
- tools/fast/aens_members.py: per member per hour, runs/aensm/<cyc>/m<NN>/mem_f<FFF>.webp. Lossless WebP, 0.5 deg (every 2nd point of the
  aens crop 333x821 -> 167x411); R = MSLP 920-1070 mb, G = 500 mb height 4600-6000 m (8 bit). Downloads only the msl + z500 GRIB ranges.
  Steps: 6-hourly to F+120, then 12-hourly to F+360 (40). It skips steps that already have 50 files, so a rerun resumes where it stopped.
  --index-only writes run.json from the files already made.
- viewer.js: model aensm in Runs ("AIFS ENS member"). A Member box (type 1-50) shows only on those runs. Files load only for the picked
  member (cache keys carry the member). Half-res fields are upsampled to the crop grid (upHalf). The run line shows "member N", and ?mem= is kept in the URL.
- studio.js: the pill reads "AIFS ENS MEMBER N". window.studioLabelHidden drops map line labels under the color bar / credit band
  (WW3 16:9 fix; it is applied at viewer paint time, so a pure Studio pan won't re-hide until the next redraw).
- index.html / studio.html: Member box + CSS. Cache tags viewer/studio ?v=20261103m1.
- Products: slp (the AIFS entry) + z500anom (the aens entry). Static layers / keys / climatology / LUTs come from the aens / aifs ones already in R2.
Data so far (/workspace/aensm_pv/data/runs/aensm): 2026110300 8 steps, 2026110306 6 steps (~1.2 MB per step for all 50 members, ~25 KB per member-hour).
Measured: one step = 100 GRIB messages, 72.9 MB, 26-126 s (data.ecmwf.int; the ECMWF AWS mirror returns 503). Est. 40 steps ~51 MB per run, ~102 MB for 2 runs.
Preview deployed with partial data: https://6e44df5f.<PAGES_PROJECT>.pages.dev (00Z F+6..30, 06Z F+6..18 at that time). QA NOT finished.
## Resume
cd live_main/tools/fast; for c in 2026110300 2026110306; do python3 aens_members.py --cycle $c --out /workspace/aensm_pv/data --man /workspace/wx-models-site/backups/ww3_waves_20261103/r2/manifest.json --workers 3; done
(maybe newer cycles by then: keep the two newest). bash /workspace/aensm_pv/build_pdata.sh <cyc1> <cyc2>
PV_PDATA=/workspace/aensm_pv/pdata bash /workspace/wx-models-site/deploy_preview.sh
QA: /workspace/aensm_qa/qa.py <preview url> (the z500anom step clicks the Upper Air tab; it was mid-run when paused)
## 11-03 ~7:05 AM PST: done (hidden preview)
Preview https://29c95c13.<PAGES_PROJECT>.pages.dev (branch aens-members, commit after c452218: + ECMWF precip-type blending).
Runs 2026110300 + 2026110306 complete, 40 steps x 50 members each; 4000 files, 86.7 MB. QA 0 errors; only the picked member's files are fetched.
