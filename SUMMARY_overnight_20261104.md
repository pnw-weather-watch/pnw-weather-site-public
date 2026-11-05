# Overnight summary — second site (hidden preview) — 2026-11-04

**Scope:** Pacific NW / California / Hawaii weather model site (PNW Cloudflare account only).  
**Production:** no new Push/Deploy after the earlier 20:44 PT promote (`2fac240f` of `bb01bc8`). Everything below is **preview only**.  
**HOLD:** do **not** build a “WA Maps” tab or WA Maps–style NBM poster graphics (logo / big titles) until Benjamin says otherwise.

---

## What a fresh Push/Deploy would promote

1. **Site code** currently on `main` (latest closeout commit below) → Cloudflare Pages production branch.  
2. **R2 data** under `preview/` that is ready to copy to live keys (via the promote path used earlier): CA widenings, AIFS/AENS/GFSW/HRRR/… runs present locally, **epsm** with CVD-safe products, **EPS** through F96, **AENS** through F120, clim slots, mkeys a80 for new CA views, etc.  
3. Production still needs Benjamin’s **Push + Deploy** phrase; do not run `deploy_site.sh --confirm` without it.

Rollback target for the last prod deploy remains **`b51db3eb`** (record `ROLLBACK_prod_b51db3eb_20261104.md`).

---

## Built / verified on the hidden preview

| Area | Notes | Key commits |
|---|---|---|
| CA views + widen | S/C/N California; Central/Northern ~2× E–W; Southern +12.5% east + 50 mi west | `ebe1766`, `92987b2` |
| SST anomaly (#16) | NOAA OISST | `61e1ed9` |
| Obs CA + HI (#17) | Presets + HI ASOS | `51cf1be` |
| Radar/sat CA+HI (#18) | MRMS CA/HI detail + GOES | `5fed335` + `radsat_*` shots |
| EPS mean / lows / CAPE (#10/#11/#19) | Theme dots for lows | `811210d`, `cb2e161` |
| Member grids / meteograms (#12/#13) | EPS mem pts + Meteograms page | `12d5698`, `70cf9da`, `8287d31` |
| epsm member maps | SLP / gust / z500anom / snow; **CVD-safe keys** | `566e288` |
| AIFS + AENS + GFS-Wave | On preview | `db1c7f9`, `1e916fb` |
| Ensemble hour extend | epsm F6–F120; EPS F3–F96; AENS F6–F120 | data + `b89ca6b` |
| Preview/live R2 split | `preview/` prefix | `dc362ad` |
| QA | Full preview guard **577 OK / 0 FAIL**; polish final **576 OK / 0 FAIL**; interaction 10/10 | `ded9016`, `5a6658e` |
| Safety | PNW-only R2/upload keys | `b4c7b3c` |

### Screenshot paths (`local/shots/20261104/`)

**Extended ensembles (retaken 23:26 PT):**  
`eps_ext_f96_t2m_pnw_{desktop,phone}.png`, `eps_ext_f96_elows_pnw_{desktop,phone}.png`,  
`aens_ext_f120_t2m_pnw_{desktop,phone}.png`,  
`epsm_ext_f120_slp_pnw_{desktop,phone}.png`, `epsm_ext_f120_snow_pnw_{desktop,phone}.png`

**Meteogram colors:** `meteograms_colors_seattle_{desktop,phone}.png` (also earlier `meteogram_colors_AFTER*`, `meteograms_page_colors_*`)

**epsm CVD products:** `epsm_{gust10,slp,snow,z500anom}_pnw_{desktop,phone}.png`

**#18 radar/sat:** `radsat_ca_{radar,ir}_{desktop,phone}.png`, `radsat_hi_{radar,gc}_{desktop,phone}.png`

**Other:** CA widen BEFORE/AFTER, SST, obs_ca/hi, ens dots, mgrid/mlines, mslpa_a80_*, offshore waves, prod_* from the earlier Push/Deploy.

### Overnight log

`OVERNIGHT_LOG_20261104.md` — chronological table for the night.

### DETAILS checklist

`local/DETAILS_CHECKLIST_ticked_20261104.md` — soft leftovers ticked where code-verified (NBM via site temp scale **not** WA Maps posters; OBS_STYLE; QPF18; passes; H/L; credits). **0 open `[ ]` / `[~]`** on that file after the polish pass.

---

## Open decisions for Benjamin

1. **PacIOOS SWAN (UH 500 m waves)** — **NEVER used** (Benjamin 11-05: Hawaii waves = ECMWF IFS open wave only).
2. **PNW town labels** — density / extra Western–Eastern WA towns already partly addressed; any further “more town labels” framing or light/dark base retune for NBM-look temps still a taste call (PRODUCT_LOOKS_PLAN).  
3. **New sources (rule 7)** already in use or pending acknowledgment:  
   - **NCEP/NCAR R1 via NOAA PSL** climatology (public domain; PSL asks for credits-page acknowledgment) — used for anomalies / MSLP normals. Confirm OK for the live site.  
   - **NDBC buoys as a forecast/wave data source** — currently **not** used as a new modeled source (map already has NDBC buoy *labels* on wave views from shipped JSON). Confirm if buoy *observations* should feed products.  
   - Optional views Bay Area / Oregon coast / Big Island-only — **shipped on preview** (11-05); taste OK for production still Benjamin’s call.
4. **WA Maps tab** — **OFF the list entirely** (Benjamin 11-05 12:16 AM: never build).
5. **NOAA WaveWatch III / GFS-Wave as a second wave source** — from Weather Bot's review; treat as a **new source** (rule 7). **Do not newly wire / expand it** until Benjamin OKs. A `gfsw` model already sits on the hidden preview from earlier overnight work — confirm keep, credit-only, or remove before Push/Deploy. Hawaii stays on **ECMWF IFS open wave** only.
6. **Push + Deploy** — say the words when preview should become production (promote `preview/` → live R2 + Pages main).

---

## Notable commits (this overnight stretch)

`61e1ed9` SST · `51cf1be` obs CA/HI · `70cf9da` / `8287d31` meteogram colors · `ebe1766` / `92987b2` CA views · `dc362ad` preview data · `811210d` / `cb2e161` EPS · `5fed335` radar/sat · `12d5698` members/mkeys · `566e288` epsm CVD · `ded9016` guard harden · `b89ca6b` extend-safe steps · `9e3abdb` closeout · *(polish commit follows)*.

Final polish-pass QA (Access token rotated for `pnw-qa`; Playwright chromium reinstalled): **FINAL_OK 576 / FINAL_FAIL 0** — `qa/guard_preview_final_20261104.log` (started 23:27 PT; all GUARD_MODELS batches OK on first attempt). Earlier full guard same night: **577 OK / 0 FAIL** (`qa/guard_preview_full_20261104.log`).


## Stretch 4 status (preview, ~02:30 PT 11-05)

- **Hawaii waves:** ECMWF IFS open wave; coast-only town numbers (1/4-mi offshore). Commits `f5ef608`, `80ef26c`.
- **Views:** Bay Area (`bay`), Oregon coast (`orco`), Big Island (`bigi`) on preview with full product support.
- **PNW towns:** 29 labels on t2m / names on mslpa (CA-like tiers).
- **Ensembles (full cadence on preview):** EPS mean **F3–F360** (84), epsm **F6–F360** (40), AENS **F6–F360** (60). `run.json` `expected` = full cadence (`298eac2`).
- **Weather Bot B (preview):** snow scale floors (≥12 in/6 h pass+meteogram; ≥3 in/h snow-rate on pass winter meteogram) `c6077eb` + `a9aae70`; ECMWF `gust3`/`gust6`; obs sat **4-hour** loop + scrubber row (~480 px); F+ badge / elows key / buoys+H/L verified in shots. No Studio/Social. Latest preview deploy `9b9598ed` (HEAD includes `ace1f05` viewStatic wait; floors `a9aae70`; HI waves/views `f5ef608`/`80ef26c`).
- **WW3 / gfsw:** open decision #5 only — not newly wired.
