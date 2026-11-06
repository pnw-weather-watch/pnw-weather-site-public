# Pre-ship checks for this site

Ported from the other site's `GUARDS.md`. Studio, social loops, TV mode, and the Washington forecast maps are not on this site, so their guard groups are not copied.

| Check | Where | What it protects | Compared with |
|---|---|---|---|
| Pass floors | `qa/pass_floors_test.py` | `MG_FLOORS` is `{passPrecipIn: 3, passSnow6In: 12}` in both `viewer.js` and `meteograms.js`, and both files actually use it. No browser. | `qa/guard.py` reloads the map and checks the URL. It never reads the axis floors. |
| Map guard | `qa/guard.py` | After a reload, run, product, and view stay. The map fits the viewport. Default desktop size is 1920×1080. The open page's `window.MG_FLOORS` matches the same 3 and 12. | The floors file checks the source. This check confirms the page that shipped still exposes that object. |

```bash
python3 qa/pass_floors_test.py
python3 qa/guard.py https://preview.example 1920x1080
```

Not copied, and why: `ship.sh`, `DEPLOY_LOCK.md`, the known-versus-new baseline, and the Studio / WA-maps refresh groups belong to the other site's deploy. This repo does not run that ship path. The frame-watcher cron stays on its own branch.
