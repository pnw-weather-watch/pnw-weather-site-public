# PREVIEW_temp_scale_green_20261105

- **Commit:** `031b544` (theme/temp_scale.json only).
- **Scope:** hidden preview only — no production deploy, no live R2 promote of site.
- **Request (Benjamin 11-05 5:54 AM PT):** darker oranges not until ~70°F; add green (teal-leaning, distinct from other-site mint) before oranges; keep blues-darken-sooner; CVD deutan/protan ΔE≥3; white-dashed freezing unchanged.
- **CVD:** warm-side optimize min rounded adjacent ΔE **3.23** (deutan/protan).
- **Preview deploy:** `02b726e2` → https://preview.pnw-weather-site.pages.dev
- **Data:** regenerated IFS/GFS t2m keys + re-encoded nbm1 packs for sample hours; synced under `preview/` prefix only.
- **QA:** `qa/guard_preview_tempscale_20261105.log` — **FINAL_OK 233 / FINAL_FAIL 2** (2 FAIL = transient refresh keeps bigi→hiw race, same class as earlier aifs phone flake; not scale).
- **Backup:** `backups/temp_scale_green_20261105/`
- **Shots:** `local/shots/20261105/tempscale_*`

## Scale stops (°F band → hex) — warm side 28–80

| °F | before | after |
|---|---|---|
| 28–30 | `#bce1e0` | `#bce1e0` |
| 30–32 | `#d1ece5` | `#d1ece5` |
| 32–34 | `#f1f3bf` | `#e6f0bb` |
| 34–36 | `#f3efaf` | `#d7eba9` |
| 36–38 | `#f5e99a` | `#bfe392` |
| 38–40 | `#f7e17e` | `#9fd978` |
| 40–42 | `#f8d66e` | `#7fce6e` |
| 42–44 | `#f8cb62` | `#5fc078` |
| 44–46 | `#f5bc54` | `#46b37c` |
| 46–48 | `#f4ad47` | `#33a67a` |
| 48–50 | `#ec9e45` | `#2ea581` |
| 50–52 | `#f0923a` | `#38b28f` |
| 52–54 | `#e88339` | `#48be8f` |
| 54–56 | `#e07536` | `#62c981` |
| 56–58 | `#d96938` | `#80d272` |
| 58–60 | `#dc5c2c` | `#a6d960` |
| 60–62 | `#d54f2e` | `#c2d954` |
| 62–64 | `#ce4530` | `#d6d34e` |
| 64–66 | `#c73d33` | `#e3ca4a` |
| 66–68 | `#c03436` | `#ecbe44` |
| 68–70 | `#b92b39` | `#eca83e` |
| 70–72 | `#af263b` | `#e48c35` |
| 72–74 | `#a3233c` | `#dc742f` |
| 74–76 | `#97203d` | `#d25e2e` |
| 76–78 | `#8b1d3e` | `#c64a30` |
| 78–80 | `#7f1a3f` | `#a83137` |

Cold side (−40…32) unchanged from blues-darken-sooner. `colors[0]` under `#1c0d33`, over `#5a0f2e`.

## Notes

- Freezing 32°F white-dashed line rules untouched (viewer/meteogram).
- Meteograms/obs that share `theme/temp_scale.json` via house_style/manifest pick up the new ramp after preview data sync.
