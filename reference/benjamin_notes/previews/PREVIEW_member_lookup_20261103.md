# Member-number lookup: ECMWF EPS members ("epsm") - 11-03-26 PST
Approved: Benjamin t2209u 11:43 AM "Go ahead and do it all, push and deploy as you check each one off the list".
Already live before this item: AIFS ENS member lookup (aensm, MSLP + 500 mb, since d37a4c3c 7:08 AM). This item adds the EPS the same way.
Hidden previews: fe99424f (00Z only, UI QA), a1aac43a (00Z + 12Z, final QA). Production: 54f5e4d7 (06aa1d8).
Commits on main (fast-forward 311ddab..06aa1d8):
  827966b eps_members.py, epsm_cycle.py, fast-models.yml matrix + epsm, viewer packs [file, channel, tile], member < > stepper + arrow up/down (wraps), Studio pill "EPS member N", ?v=20261103ml1
  06aa1d8 snow total range 0-200 in (80 in clipped coastal BC mountains at long range)
How it works: Runs menu "EPS member 12Z 11-03" -> Member box (type 1-50, < >, or arrow up/down with focus off the menus). Only that member's file for the
hour is fetched (one ~60 KB lossless WebP per member-hour: tile 0 = MSLP / 500 mb height / 10 m gust, tile 1 = snow total). ?mem=N kept in the URL.
Products: Sea-Level Pressure (isobars, H/L), 500 mb Height Anomaly, 10 m Wind Gusts, Snowfall Total (10:1). Hours 6-hourly to F+120, then 12-hourly to F+360.
Works in the main viewer (desktop + phone) and Studio (9:16 + 16:9). Not in Compare.
Limits: 0.5 deg (half the EPS mean maps' resolution, upsampled); gust is ECMWF's own window (1 h to F+90, 3 h to F+144, 6 h after; said in the map
subtitle), not a 6 h max; no 6/12/24/48 h snow windows (total only); no lows list / precip type per member; 00Z and 12Z runs only (06Z/18Z EPS stops at F+144).
Storage: ~121-124 MB per run, newest 2 runs kept -> ~245 MB in R2. R2 Class A: 2000 puts per run x 2 runs/day = ~4k/day (~120k/month, ~+12 %
on the ~1.0M/month estimate in LIMITS_20261031; overage if any is cents). Reads: 1 per member-hour viewed.
Runtime: box 1238 s (00Z, 3 workers) / 1361 s (12Z, 4 workers) per full run, 3.4 GB of GRIB byte ranges read per run. Workflow job: see ROLLBACK note.
QA (preview + production): 0 console/page errors, 0 bad /d/ responses, desk + phone; requests only for the picked member; stepper/arrows/wrap 50->1/typed
member all OK; other models + aensm unchanged; smoke viewer/compare/social/wamaps/meteograms/studio 0 errors.
Screens: /workspace/member_qa/pv/ (preview), /workspace/member_qa/prod/ (production), /workspace/member_qa/pv_early/.
