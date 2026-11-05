import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'qa')); from _access import scope_sync
import os
from playwright.sync_api import sync_playwright
B="https://preview.pnw-weather-site.pages.dev/index.html"
H={"CF-Access-Client-Id":os.environ["QA_ACCESS_CLIENT_ID"],"CF-Access-Client-Secret":os.environ["QA_ACCESS_CLIENT_SECRET"]}
with sync_playwright() as p:
    b=p.chromium.launch(); c=scope_sync(b.new_context(viewport={"width":1440,"height":900})); pg=c.new_page()
    pg.goto(B,wait_until="commit"); pg.wait_for_timeout(8000)
    print("buttons:",[t.strip() for t in pg.locator("button, a").all_inner_texts() if t.strip()][:40])
    print("WA Maps in page:", "WA Maps" in pg.content())
    print("views:", pg.locator("#view option, select option").all_inner_texts()[:60])
    b.close()
