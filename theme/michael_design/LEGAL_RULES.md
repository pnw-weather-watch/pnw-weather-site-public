# Legal rules for this site (standing rulebook)

Started Tue Nov 3, 2026, 12:45 PM PST from Benjamin's instructions ("Make sure everything is legal to be used in a monetized channel, the less credit lines the better"; "Keep only the credits we legally need to show, only use data we can legally access for free. Create rules for yourself as we go."). Add a dated line under **Change log** whenever a rule changes.

1. **Free and legal access only.** Use only data and assets that can be downloaded free of charge from the provider's public endpoint without signing in, for example NOAA NOMADS/AWS, data.ecmwf.int, census.gov and naturalearthdata.com. No paid APIs, no paid tiers, and no ECMWF service agreements or other paid delivery.
2. **No scraping behind logins, and nothing the terms block.** Do not scrape pages that need an account. Do not use sources whose terms forbid automated access or redistribution. Keep within published rate limits.
3. **Commercial use must be allowed.** The site and its images may be monetized. Only use public domain, CC0, CC BY, SIL OFL, or terms that explicitly allow commercial use.
4. **No non-commercial or share-alike terms.** Never use NC (CC BY-NC*), SA (CC BY-SA*, ODbL), "personal use only", "research only", or any license that would bind our own images. This rules out OpenStreetMap-derived data (ODbL) and most Wikipedia text.
5. **Show only the credits the law requires on images.** Today that means ECMWF only (CC BY 4.0 plus ECMWF Terms of Use): the "based on data and products of ECMWF" wording, (modified), © year ECMWF, the license link, and the disclaimer. Public-domain sources (NOAA, US Census TIGER, USGS, Natural Earth) and OFL fonts get no on-image credit.
6. **Everything else goes in `CREDITS_LEGAL.md`,** and from there onto the site's About/Credits page, including the full ECMWF service wording.
7. **Verify before adding.** Before adding any new source, dataset, font, icon or other asset, read its terms on the real source page. Record the license, whether commercial use is allowed, the URL and the date checked in `CREDITS_LEGAL.md`. If the terms are unclear, don't use it and ask Benjamin.
8. **Don't imply endorsement.** No NOAA/NWS, USGS, Census or ECMWF logos, and no wording that suggests our output is official or endorsed. Modified model data is never presented as official government material.
9. **Trademarks:** route markers are used only to identify the real route they stand for. "TIGER/Line" is never used in a product name.
10. **Re-check when providers change.** If a provider changes its license page or data portal, re-verify and update the date in `CREDITS_LEGAL.md`.

11. **Original look only.** Do not copy color tables, images, code, logos or branding from other model sites (his current site, Pivotal, Tropical Tidbits, WeatherBell, weather.us, COD, Meteociel, Windy, etc.). Our scales are designed in-house and checked against the avoid list in `MODEL_SITE_SURVEY.md`. Looking at what products they offer is fine.

## Change log
- 2026-11-03 12:45 PM PST: rules 1-10 created; applied to pass view v5.
- 2026-11-03 4:05 PM PST: rule 11 added (original palettes and look; Benjamin asked for vivid, original colors).

- **11a. No third-party palettes (added Tue Nov 3, 2026):** never copy another site's color table, scale or band steps. We may sample or view them only to compare and stay distinct, and nothing sampled is used on a published map. Keep each product's look checkably different from the big subscription sites (WeatherBell, etc.); see `WEATHERBELL_COMPARISON_v1.md`.
- Change log: Tue Nov 3, 2026 ~5:05 PM PST, added 11a after Benjamin's WeatherBell request.
- Change log: Tue Nov 3, 2026 ~6:20 PM PST. The site's anomaly maps must use `design/anom_scale.json` (an original palette, rule 11a). Don't swap in any third-party anomaly color table.
