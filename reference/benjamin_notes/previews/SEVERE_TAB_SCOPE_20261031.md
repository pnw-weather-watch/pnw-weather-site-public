# Severe tab for HRRR / RRFS - scope (research only, 10-31-26 ~9:25 AM PT)
Benjamin 9:15 AM: "For the weather website for the hrrr and RRFS, please add simulated radar + updraft helicity. I also want helicity
streaks. 0-3km cape, surface cape, lapse rates, all these can be put under a severe tab."
Nothing built. Sources checked live: HRRR wrfsfcf06 .idx (12Z 10-31, 173 records), RRFS 2dfld f006 / f060 and prslev f006 .idx (12Z 10-31).

## What is already there vs. new
| Field | HRRR (wrfsfc) | RRFS | On the fast site now? |
|---|---|---|---|
| Simulated radar (composite reflectivity) | REFC:entire atmosphere | REFC (2dfld) | YES, `refc` "Composite Reflectivity", under the **Precip** tab -> just list it in Severe too (no data work) |
| Surface CAPE | CAPE:surface | CAPE:surface (2dfld) | YES, `sbcape`, already in the **Severe** tab |
| MUCAPE, lightning | CAPE 255-0 mb, LTNG | same | YES (Severe tab: mucape, ltng, ltng6) |
| 2-5 km updraft helicity (hourly max) | MXUPHL:5000-2000 m, "N-1 to N hour max" every hour | MXUPHL:5000-2000 m (2dfld) hourly to F48; after F48 (3-hourly files) only the last hour of each 3 h ("59-60 hour max") | NO - new field `uh` |
| Helicity streaks / swaths (run-total max UH) | built from the hourly MXUPHL (running max over the run) | same; past F48 the swath misses 2 of every 3 hours (file gap) | NO - new field `uhs` (running max, made in the encoder so the browser does not need every earlier hour) |
| 0-3 km CAPE | CAPE:0-3000 m above ground | CAPE:0-3000 m (2dfld) | NO - new field `cape3` |
| 700-500 mb lapse rate | TMP + HGT 700 / 500 mb (in wrfsfc) | TMP + HGT 700/500 in **prslev** (pipeline already reads prslev for t700/t500) | t700 + t500 already stored; z700 is not. New field `lr75` (C/km) made in the encoder |
| 0-3 km lapse rate | TMP 2 m + surface HGT + TMP/HGT at 1000/925/850/700 mb -> T at 3 km AGL by interpolation in height | same (prslev) | NO - new field `lr03` |
| Bonus, free in the same files | HLCY 0-3 / 0-1 km (storm-relative helicity), VUCSH/VVCSH 0-6 km shear, MXUPHL 0-3 km | same | not asked; could ride in the spare pack channel |

## Plan
1. Encoder (fast_encode.py): fields uh, uhs (running max kept in the cycle state), cape3, lr03, lr75; two new 3-channel packs
   (`svr`: uh, uhs, cape3; `lapse`: lr03, lr75, + srh03 or empty). Byte-range reads of ~6 more GRIB messages per step.
2. Products: "2-5 km Updraft Helicity" (hourly max, m2/s2, SPC-style 25/50/75/100/150/200+ colors over radar-grey), "UH Streaks"
   (run max to the valid time, swath colors), "Radar + UH" combo (refc fill + UH contours, the Pivotal look), "0-3 km CAPE",
   "700-500 mb Lapse Rate", "0-3 km Lapse Rate" (C/km, 6.5-9.5 highlighted). Severe tab order: refc, Radar+UH, UH, UH streaks,
   sbcape, mucape, cape3, lr03, lr75, ltng, ltng6 (ECMWF/EPS keep their current Severe items). Color keys published with publish_static.
3. Viewer: TABS "svr" list + refc listed in both Precip and Severe (tab logic picks the first - small change), UH contour overlay drawer.
4. Backfill the newest HRRR + RRFS run on the box so it shows at once; QA all 8 HRRR/RRFS views, desktop + phone 390.

## Cost
- R2: measured pack sizes today (F18 12Z): HRRR conv pack 96 KB, RRFS 136 KB; aloft 257/310 KB. Two new packs (mostly
  zero UH compresses well) ~ 0.25-0.4 MB per step -> HRRR 48 steps ~ 12-19 MB/run, RRFS 60 steps ~ 15-24 MB/run.
  With the runs kept (newest 2 + 3-day expiry, ~4 runs each in R2) about +0.12-0.17 GB total.
- Workflow: a few more byte-range GRIB reads per step (HRRR already reads ~40 messages per step): est. +10-15 % per HRRR/RRFS step,
  roughly +1-3 min per run. Not measured yet. Actions minutes are free (public repo); the runner slot is the only limit.
- Hours: encoder fields + packs 3-4 h, products / color keys / static publish 2 h, viewer tab + Radar+UH overlay 2-3 h,
  backfill + QA 2 h -> **9-11 h** (one session), hidden preview first.

## R2 room (measured 10-31 ~9:25 AM PT, bucket <R2_BUCKET>, full listing)
24,943 objects, **3.25 GB (3.02 GiB) of the 10 GB free tier -> about 6.75 GB left**.
static 0.64, gfs 0.55, ifs 0.46, rrfs 0.44, aifs 0.38, hrrr 0.33, eps 0.18, nbm 0.13, aens 0.11, ifs9 0.05 GB.
Per run: gfs 136 MB, ifs 114, rrfs 109, aifs 94, hrrr 81, eps 59, aens 53, ifs9 53, nbm 32 MB.
