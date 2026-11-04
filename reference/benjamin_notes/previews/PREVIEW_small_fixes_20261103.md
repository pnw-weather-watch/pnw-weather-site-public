# Hidden preview: small fixes batch + thin 2 mb isobars (11-03-26 ~12:20 PM PST)
Preview: https://7ac92523.<PAGES_PROJECT>.pages.dev (first build 5fdbbcce had a Social data-path bug, fixed in 311ddab). Production then: 76b8a5d0 (f536a6b).
Branch small-fixes (worktree /workspace/wx-models-site/smallfix) on origin/main f536a6b:
  bb73482 snow_map corner tag follows the model (cherry-pick of 79f7d63)
  ed4b9cb Social tab hour scrubber
  defe102 lows-list member dedupe, Mem label vs mean L, wave line labels vs coast/buoy labels, Studio header/F+ badge label hiding
  778e66c MSLP isobars every 2 mb, 0.75 pt lines, 1.6 pt halo (Benjamin 11-03 via parent)
  311ddab Social: plain social.js src (build.sh WX_DATA injection needs the exact tag)
Per fix:
1. Relay dedupe: SKIPPED (alert relay = alert pipeline, out of scope for this site batch; the box-side resync after a gap shipped 10-31).
2. EPS "duplicate Mem 45": one member with 2+ lows in view was listed twice. "10 strongest" = each member's deepest low, "10 weakest" = each member's weakest. QA: 0 duplicates over every hour, EPS + AIFS ENS, PNW + NA, desktop + phone.
3. Snow map tag: tools/wa_maps/snow_map.py render_special uses MODEL_TAG_OVR (NBM/EPS/EPS90 no longer say [ECMWF 0.25°]). Box Python tool, not part of the Pages build; py_compile OK, not re-rendered.
4. Wave labels: swell-period line labels slide along their line off town/buoy label boxes (dry-run of drawCoast), else dropped (no cut gap). Studio also hides line labels under the header block and F+ badge (bottom bar band already hidden since c452218).
5. EPS lows "Mem N · mb" label: candidate spots tested against all mean-L boxes, the list box, the dot key and the map edge; least-overlap fallback. QA: overlap 0 on every hour (EPS, AIFS ENS; PNW, NA; desktop + phone).
6. Social hour scrubber: slider + < > under the menu bar, label "F+N · day time PT (k/n)"; JPG while dragging, 4K PNG on release; menu/strip/arrow keys stay in sync.
7. Isobars: every MSLP isobar layer (slp, mslpqpf, ptype, thick, aifswind, mslpa, elows means) every 2 mb, lw 0.75, halo 1.6, sigma unchanged; legend text "every 2 mb". Site-side override in allProds (manifest untouched). Social stills are pre-rendered on the box and keep 4 mb until a Social re-run.
QA: 0 console errors on every page; /d/ data responses OK; smoke (viewer, compare, studio, social, wamaps, desk + phone, instant loop MP4) all 0 errors.
Screens: /workspace/small_fixes_qa/ (desk_*, phone_*, studio_*; baseline production shots in base/).
