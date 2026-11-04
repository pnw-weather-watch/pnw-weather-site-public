# AIFS ENS member lookup parity with EPS members (aensm) - 11-03-26 PST
Ask: Benjamin t2221u "I wanted this for AIFS ... build it out for AIFS" (push/deploy OK per t2209u).
What AIFS members were missing vs EPS members: products. Before: MSLP + 500 mb anomaly only. Now: Sea-Level Pressure, 500 mb Height Anomaly,
MSLP + 10 m Wind (barbs kt, color mph; AIFS ENS open data has no gust field, so 10 m wind replaces EPS's 10 m gust), Snowfall Total (10:1, from AIFS sf).
Already equal before: Member box + < > stepper, arrow up/down (wraps 50 -> 1), typed member, ?mem=, Studio pill, only picked member fetched, 40 hours, 11 views.
Format: one 2-tile 0.5 deg lossless WebP per member per hour, runs/aensm/<cyc>/mNN/mx_fFFF.webp (t0 MSLP, 500 mb, snow | t1 u10, v10). ~73 KB.
Code: commit 74beb7e on main (tools/fast/aens_members.py, aensm_cycle.py; rebased clean onto 9555dc5 radar/GOES, no conflicts). No site code change.
Hidden previews: ccae10c8 (early, partial data), d9653ad9 (final, SRC=aifsmem + pdata 06Z/12Z).
QA preview + production (desk 1440x900@2, phone 390x844@3, Studio 9:16 + 16:9): 0 page/console errors, 0 bad responses; stepper/arrows/wrap/typed/?mem= OK;
requests only for the picked member's mx_ file; Snowfall Total + MSLP + 10 m Wind render; EPS members, AIFS ENS mean, other pages smoke 0 errors.
Screens: /workspace/aifs_member_qa/pv (preview), /workspace/aifs_member_qa/prod (production), /workspace/aifs_member_qa/pv_early.
Where: Runs menu "AIFS ENS member 12Z 11-03" -> Member box; Product menu now has MSLP + 10 m Wind (Surface) and Snowfall Total (10:1) (Snow).
Cost: ~152 MB per run (was ~87 MB), newest 2 runs kept -> ~305 MB R2 (+ ~87 MB of old mem_ files in 06Z/12Z until those runs are pruned).
R2 Class A unchanged per cycle (2000 puts per run; one-time backfill 4002 puts + manifest). GRIB read per run ~5.8-6.0 GB (was ~2.9 GB), public repo Actions minutes free.
Credits unchanged: ECMWF (CC BY 4.0, "Modified"), GeoNames CC BY 4.0, Natural Earth.
Rollback: ROLLBACK_aensm_parity_20261103.md (also linked from ROLLBACK_prod_3a382136_20261103.md).
