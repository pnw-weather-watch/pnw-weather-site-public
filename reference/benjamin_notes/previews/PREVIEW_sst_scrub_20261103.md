# 11-03 hidden previews (no push / deploy / production R2 writes)
## SST anomaly (branch sst-anom on main fd5108d) — https://6624166f.<PAGES_PROJECT>.pages.dev
- NOAA OISST v2.1 (NCEI, public domain), daily 10-20..11-02 (11-02 preliminary), vs 1991-2020 normal; Waves tab; site-shipped pdata (/workspace/sst_pv/pdata, 5.2 MB)
- commits: adabed3 (rebased oisst), coast-aware sampling + newest day + Studio date badge, Runs label "daily"
- QA /workspace/sst_qa/final (0 errors)
- SSH: not built (no clean PD anomaly source chosen yet; see report)
## Studio scrubber parity (branch studio-scrub on main) — https://69b51498.<PAGES_PROJECT>.pages.dev
- bar pinned: tabs reserve ECMWF's 7-tab width, Product/View/Runs menu widths fixed, Member box floats in tab space (desktop) / keeps a slot (phone),
  loading note floats, hour readout fixed 212 px; studio.js ?v=20261103t6
- QA /workspace/scrub_qa/final (+ before/): frames + scrubber px-identical across 10 models at 1024/1280/1440/1920/390
