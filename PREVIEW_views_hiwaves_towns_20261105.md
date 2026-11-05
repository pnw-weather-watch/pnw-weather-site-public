# Preview note — HI ECMWF waves, new views, PNW towns, ensembles (11-05 ~12:40 AM PT)

**Preview only.** No production deploy. WA Maps is **off the list entirely** (never build).

## Changes
1. **Hawaii waves:** Maps + coast-town numbers use **ECMWF IFS open wave (WAM 0.25°)**, same 1/4-mile offshore sampling as the mainland (where the grid allows). PacIOOS never used. NWPS nearshore no longer preferred for HI town numbers (`viewer.js` `offVal`).
2. **New views** in `regions/regions.json`: **Bay Area** (`bay`), **Oregon coast** (`orco`), **Big Island** (`bigi`) — product support via `model_views`, coast upright, region_towns + coast labels.
3. **PNW town labels:** `region_towns.pnw` sized like California (`[[500000,100000,30000],60]`); IFS/GFS static now place **29** town numbers on `pnw` (was 0). Applies to t2m (numbers) and mslpa (names).
4. **Ensembles:** epsm extended to **F6–F240** (30 steps). EPS mean encoding toward F240 (files past F210; run.json merge as unbroken prefix grows). AENS already F240.

## Screenshots
`local/shots/20261105/` BEFORE_* then AFTER_* (desktop + phone).

## Open / deferred
- Push+Deploy still required for production.
- Optional denser Bay / Big Island labels if Benjamin wants more.
