# tide-archive (data branch)

Conditional Prediction snapshots for the PNW Weather Tides page (`tide/`), written every 6 h (02/08/14/20 UTC) by
`.github/workflows/tide-archive.yml` running `tools/fast/tide_archive/tide_archive.py`. Public NOAA data only
(CO-OPS predictions / water levels, STOFS-2D-Global). `v1/index.json` lists the months per station;
`v1/<station>/<YYYY-MM>.json` holds the issues. Snapshots before the live job started are marked `kind: "hindcast"`.
