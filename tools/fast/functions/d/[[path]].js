// GET/HEAD /d/<key> -> R2 bucket pnw-models-data (binding DATA). The whole host is behind Cloudflare Access.
// Cache: run frames are immutable for a year (run + step are in the key). Manifests, per-model catalogs
// and run.json are 30 s. Static layers are 1 day.
// Every request is one Pages Function invocation. The free plan allows 100,000 of those a day for the
// whole account (https://developers.cloudflare.com/pages/functions/pricing/). The viewer therefore
// prefetches only the next 3 hours and polls the small manifest index, not every frame.
// Production (pnw-weather-site.pages.dev) reads the live keys only.
// Every other host reads one prefix, then the live key. The prefix is WX_DATA_PREFIX when that env
// var is set (preview-pr16, or preview-pr16/). A Pages alias preview-pr16.pnw-weather-site.pages.dev
// maps to preview-pr16/ on its own. Anything else, including preview.pnw-weather-site.pages.dev, uses preview/.
const PROD_HOST = "pnw-weather-site.pages.dev";
const PAGES_TAIL = ".pnw-weather-site.pages.dev";
function normalizeDataPrefix(raw) {
  if (raw == null) return "";
  let p = String(raw).trim();
  if (!p) return "";
  if (!p.endsWith("/")) p += "/";
  return /^preview(-[a-z0-9][a-z0-9-]*)?\/$/.test(p) ? p : "";
}
export function dataPrefix(hostname, env) {
  if (hostname === PROD_HOST) return "";
  const fromEnv = normalizeDataPrefix(env && env.WX_DATA_PREFIX);
  if (fromEnv) return fromEnv;
  const sub = hostname.endsWith(PAGES_TAIL) ? hostname.slice(0, -PAGES_TAIL.length) : "";
  if (/^preview-pr\d+$/.test(sub)) return sub + "/";
  return "preview/";
}
export async function onRequest({ request, params, env }) {
  if (request.method !== "GET" && request.method !== "HEAD") return new Response("method not allowed", { status: 405 });
  const key = [].concat(params.path || []).join("/");
  // preview/ and preview-<name>/ are data areas, not viewer paths. Production must not be able to
  // read them by asking for the prefixed key as if it were live.
  if (!key || key.includes("..") || key.startsWith("preview/") || key.startsWith("preview-") || !env.DATA) return new Response("not found", { status: 404 });
  const prefix = dataPrefix(new URL(request.url).hostname, env);
  const opts = { onlyIf: request.headers, range: request.headers };
  let obj = prefix ? await env.DATA.get(prefix + key, opts) : null;
  if (!obj) obj = await env.DATA.get(key, opts);
  if (!obj) return new Response("not found", { status: 404 });
  const h = new Headers(); obj.writeHttpMetadata(h); h.set("etag", obj.httpEtag);
  if (obj.uploaded) h.set("last-modified", obj.uploaded.toUTCString());   // meteograms page "Updated" stamp
  const meta = key === "manifest.json" || key === "manifest.index.json" || key.startsWith("models/") || key.endsWith("/run.json") || key.endsWith("/run_x.json");
  h.set("cache-control", meta ? "private, max-age=30" : key.startsWith("runs/") ? "private, max-age=31536000, immutable" : "private, max-age=86400");
  const status = request.headers.has("range") && obj.range ? 206 : 200;
  if (!("body" in obj) || !obj.body) return new Response(null, { status: 304, headers: h });
  if (request.method === "HEAD") return new Response(null, { headers: h });
  // Leave the bytes plain. The edge already negotiates gzip and brotli, and the browser
  // undoes that before response.json(). A Content-Encoding set here was decoded again
  // (or not at all) on the preview host, so both the index and manifest.json failed to
  // parse and the page never reached the menus.
  if (meta && !(h.get("content-type") || "").includes("json")) h.set("content-type", "application/json");
  return new Response(obj.body, { status, headers: h });
}
