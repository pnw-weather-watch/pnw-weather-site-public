"""Scope the Cloudflare Access service-token headers to the preview/prod Pages host ONLY.
Playwright's extra_http_headers is sent on every request the page makes, including third-party origins (IEM, NWS, ...), which
would leak the QA token and break their CORS. Use scoped_ctx()/scope_sync()/scope_async() instead (values never printed)."""
import os
HOSTS = ["https://*.pnw-weather-site.pages.dev/**", "https://pnw-weather-site.pages.dev/**"]
def hdr():
    return {"CF-Access-Client-Id": os.environ.get("QA_ACCESS_CLIENT_ID", ""), "CF-Access-Client-Secret": os.environ.get("QA_ACCESS_CLIENT_SECRET", "")}
def scope_sync(ctx):
    H = hdr()
    for u in HOSTS: ctx.route(u, lambda r: r.continue_(headers={**r.request.headers, **H}))
    return ctx
async def scope_async(ctx):
    H = hdr()
    async def h(r): await r.continue_(headers={**r.request.headers, **H})
    for u in HOSTS: await ctx.route(u, h)
    return ctx
