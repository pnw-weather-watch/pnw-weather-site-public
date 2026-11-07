// Run / product / view restoration for the fast viewer.
// Pure functions (no DOM) so a refresh can keep a supported choice, and an unsupported one
// falls back the same way every time instead of whatever the address bar still said.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.WXSelect = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // Color-key path for this product and view, or null when the manifest has none.
  // A missing key must not throw: the map can still be drawn, and the choice can still be saved.
  function lookupKey(product, view, vid, pid) {
    if (!product) return null;
    const K = product.keys || {};
    const V = view || {};
    const src = V.src || vid;
    const raw = (V.keys && pid && V.keys[pid]) || (src && K[src]) || (V.keysFrom && K[V.keysFrom]) || K.wa;
    return typeof raw === "string" && raw ? raw : null;
  }

  // Climatology blend weights, same months (and 00/06/12/18Z hours) as climAt.
  // Indexes that are not in both files and ranges are dropped so nothing fetches "undefined".
  // null = this model has no climatology for the variable. [] = the valid time has no slot.
  function climParts(clim, validIso) {
    if (!clim || !Array.isArray(clim.files) || !Array.isArray(clim.ranges)) return null;
    const n = Math.min(clim.files.length, clim.ranges.length);
    const ok = i => Number.isInteger(i) && i >= 0 && i < n && clim.files[i] && clim.ranges[i] != null;
    const v = new Date(validIso);
    if (Number.isNaN(v.getTime())) return [];
    const mo = v.getUTCMonth();
    const mid = Date.UTC(v.getUTCFullYear(), mo, 15);
    const m2 = (mo + (v.getTime() >= mid ? 1 : -1) + 12) % 12;
    const w = Math.min(1, Math.abs(v.getTime() - mid) / (30.4 * 86400e3));
    let parts = [[mo, 1 - w], [m2, w]];
    if (clim.hours) {
      const hx = (v.getUTCHours() + v.getUTCMinutes() / 60) / 6;
      const h0 = Math.floor(hx) % 4, h1 = (h0 + 1) % 4, wh = hx - Math.floor(hx);
      parts = parts.flatMap(([k, wk]) => [[k * 4 + h0, wk * (1 - wh)], [k * 4 + h1, wk * wh]]);
    }
    return parts.filter(p => p[1] > 1e-6 && ok(p[0]));
  }

  // Tighter frame -> the wider frame it sits in. A model that lacks the chosen view
  // shows the nearest parent (high-res Pacific Northwest -> Pacific Northwest) with no toast.
  const VIEW_PARENT = {
    pnwwide: "pnwhr", pnwhr: "pnw", pnwt: "pnw", pnw: "na", pac: "na",
    passes: "pnwhr", puget: "wa", wwa: "wa", ewa: "wa", newa: "wa", lm: "wa", wa: "pnwhr", bc: "pnw",
    orco: "pnwt", bay: "norca", norca: "ca", cenca: "ca", socal: "ca", capasses: "ca",
    bigi: "hiw", hiw: "pac", wc: "pnw",
  };

  function pickView(views, usable, requested) {
    const has = (list, id) => list.some(v => v.id === id);
    if (has(usable, requested)) return requested;
    const seen = new Set();
    let id = requested;
    while (VIEW_PARENT[id] && !seen.has(id)) {
      seen.add(id);
      id = VIEW_PARENT[id];
      if (has(usable, id)) return id;
    }
    const pref = ["pnw", "pnwhr"];
    return pref.find(x => has(usable, x)) || (usable[0] && usable[0].id)
      || pref.find(x => has(views, x)) || (views[0] && views[0].id) || requested;
  }

  // User-facing names only. A raw id (pnwhr, t2ma) is never shown.
  function publicName(text, fallback) {
    const s = text == null ? "" : String(text).trim();
    if (!s || /^[a-z0-9][a-z0-9_-]*$/.test(s)) return fallback;
    return s;
  }

  // products: available on this run, in menu order, {id, title, tab}
  // views: model views in menu order, {id, label, waveOnly}
  // Returns {prod, view, note, prefer, changed}. note is a product or wave-only message.
  // A view this model does not have is silent: prefer stays the chosen id so the next model can restore it.
  function resolveSelection(o) {
    const products = o.products || [];
    const views = o.views || [];
    const reqProd = o.prod;
    const reqView = o.view;
    let prod = products.some(p => p.id === reqProd) ? reqProd : null;
    let prodNote = null;
    if (!prod) {
      const tab = o.currentTab || (o.tabOf && o.tabOf(reqProd));
      const own = o.tabOf && o.tabOf(reqProd);
      const pick = products.find(p => p.tab === tab) || products.find(p => p.tab === own) || products[0];
      prod = pick ? pick.id : reqProd;
      const got = publicName(pick && pick.title, "another product");
      const asked = publicName(o.prodTitle, "That product");
      prodNote = `${asked} isn't in this run. Showing ${got}.`;
    }
    const wavy = o.isWave ? o.isWave(prod) : false;
    const usable = views.filter(v => wavy || !v.waveOnly);
    const wanted = o.prefer || reqView;
    const view = pickView(views, usable, wanted);
    let viewNote = null;
    if (view !== wanted) {
      const reqV = views.find(v => v.id === wanted);
      // The view exists here but only for wave maps. A view this model does not have
      // falls back silently (no overlay, and never the internal id).
      if (reqV && reqV.waveOnly && !wavy) {
        const gotV = views.find(v => v.id === view);
        viewNote = `${publicName(reqV.label, "That view")} is only for wave maps. Showing ${publicName(gotV && gotV.label, "another view")}.`;
      }
    }
    const note = [prodNote, viewNote].filter(Boolean).join(" ") || null;
    return { prod, view, note, prefer: wanted, changed: prod !== reqProd || view !== reqView };
  }

  // Cascade passes: tools/forecast/temp_maps.py WA_PASSES (label, lat, lon, elev ft).
  const WA_PASSES = [
    { id: "Snoqualmie Pass", label: "Snoqualmie", lat: 47.4245, lon: -121.4136, elev: 3022 },
    { id: "Stevens Pass", label: "Stevens", lat: 47.7465, lon: -121.0854, elev: 4061 },
    { id: "White Pass", label: "White", lat: 46.6383, lon: -121.3911, elev: 4500 },
    { id: "Chinook Pass", label: "Chinook", lat: 46.8714, lon: -121.5156, elev: 5430 },
    { id: "Blewett Pass", label: "Blewett", lat: 47.3348, lon: -120.5786, elev: 4102 },
    { id: "Sherman Pass", label: "Sherman", lat: 48.6055, lon: -118.4636, elev: 5575 },
    { id: "Satus Pass", label: "Satus", lat: 45.9847, lon: -120.6536, elev: 3107 },
    { id: "Wauconda Pass", label: "Wauconda", lat: 48.7262, lon: -118.9595, elev: 4310 },
    { id: "Disautel Pass", label: "Disautel", lat: 48.2818, lon: -119.1434, elev: 3252 },
  ];

  // Imagery and categorical fills: a single number at the pass is not a useful readout.
  const PASS_NAME_ONLY = { refc: 1, refuh: 1, ir: 1, ptype: 1, prt: 1, spag: 1 };

  function passUnit(pid, P) {
    if (!pid || PASS_NAME_ONLY[pid] || (P && P.fill === "prt")) return null;
    const fmt = P && P.fmt;
    if (fmt === "in2" || fmt === "in1" || fmt === "in1s") return "\"";
    if (fmt === "ft100") return " ft";
    if (fmt === "vis") return " mi";
    if (/^gust/.test(pid)) return " mph";
    if (/^(t2m|feels|d2m|nmaxt|nmint|ehigh|elow)/.test(pid) || pid === "t2ma") return "\u00b0F";
    if (/^t\d/.test(pid)) return "\u00b0C";
    if (/^(slp|mslp)/.test(pid) && pid.indexOf("qpf") < 0) return " mb";
    if (/^(tcc|fog|ep32|ntstm|qpfa|qpfpct)/.test(pid)) return "%";
    if (/^(w500|w250|w300|w850)/.test(pid)) return " kt";
    if (pid === "aifswind") return " mph";
    if (/^(waves|wavemax|wavemax24|swellhs)/.test(pid)) return " ft";
    if (pid === "swper") return " s";
    if (/cape/.test(pid)) return " J/kg";
    return "";
  }

  function formatPassValue(pid, P, v) {
    if (!Number.isFinite(v)) return null;
    const unit = passUnit(pid, P);
    if (unit === null) return null;
    const fmt = P && P.fmt;
    let num;
    if (fmt === "in2") num = v < 0.005 ? "0" : v.toFixed(2);
    else if (fmt === "in1" || fmt === "in1s") {
      if (Math.abs(v) < 0.05) num = "0";
      else {
        const a = Math.abs(v) < 10 ? Math.abs(v).toFixed(1) : Math.abs(v).toFixed(0);
        num = fmt === "in1s" && v < 0 ? "-" + a : a;
      }
    } else if (fmt === "vis") num = v >= 7 ? "7+" : (v < 3 ? v.toFixed(1) : v.toFixed(0));
    else if (fmt === "ft100") num = String(Math.round(v / 100) * 100);
    else num = String(Math.round(v));
    return num + unit;
  }

  function passCaption(label, valueText) {
    return valueText ? label + " " + valueText : label;
  }

  // regions/regions.json CA_PASSES. Short label is what the map draws; Sonora collides with the town of Sonora.
  const CA_PASSES = [
    { id: "Black Butte Summit", label: "Black Butte", route: "I-5", lat: 41.3546, lon: -122.3539, elev: 3912 },
    { id: "Yuba Pass", label: "Yuba", route: "SR-49", lat: 39.61741, lon: -120.48995, elev: 6710 },
    { id: "Donner Pass", label: "Donner", route: "I-80", lat: 39.33987, lon: -120.34396, elev: 7239 },
    { id: "Mount Rose Summit", label: "Mount Rose", route: "NV-431", lat: 39.31325, lon: -119.89659, elev: 8911 },
    { id: "Echo Summit", label: "Echo", route: "US-50", lat: 38.81297, lon: -120.0302, elev: 7382 },
    { id: "Luther Pass", label: "Luther", route: "SR-89", lat: 38.78686, lon: -119.94686, elev: 7740 },
    { id: "Carson Pass", label: "Carson", route: "SR-88", lat: 38.6938, lon: -119.98853, elev: 8574 },
    { id: "Ebbetts Pass", label: "Ebbetts", route: "SR-4", lat: 38.54436, lon: -119.81186, elev: 8736 },
    { id: "Sonora Pass", label: "Sonora", route: "SR-108", lat: 38.3277, lon: -119.63685, elev: 9624 },
    { id: "Tioga Pass", label: "Tioga", route: "SR-120", lat: 37.91104, lon: -119.25794, elev: 9945 },
    { id: "Walker Pass", label: "Walker", route: "SR-178", lat: 35.66246, lon: -118.02675, elev: 5250 },
    { id: "Tehachapi Pass", label: "Tehachapi", route: "SR-58", lat: 35.10219, lon: -118.2837, elev: 3771 },
    { id: "Tejon Pass", label: "Tejon", route: "I-5", lat: 34.80137, lon: -118.87539, elev: 4144 },
  ];

  function passesForView(view, caPasses) {
    if (view === "passes") return WA_PASSES;
    if (view === "capasses") return caPasses || CA_PASSES;
    return [];
  }

  // HRRR / RRFS 3 km Lambert. Origin is the GRIB first grid point (NOAA HRRR mass grid).
  const HRRR_LCC = { lon0: -97.5, lat0: 38.5, lat1: 38.5, R: 6371229, dx: 3000, lon00: -122.719528, lat00: 21.138123 };
  function lambertXY(lon, lat, p) {
    const rad = Math.PI / 180, n = Math.sin(p.lat1 * rad);
    const F = Math.cos(p.lat1 * rad) * Math.pow(Math.tan(Math.PI / 4 + p.lat1 * rad / 2), n) / n;
    const rho = la => p.R * F / Math.pow(Math.tan(Math.PI / 4 + la * rad / 2), n);
    const rho0 = rho(p.lat0), th = n * (lon - p.lon0) * rad, r = rho(lat);
    return [r * Math.sin(th), rho0 - r * Math.cos(th)];
  }
  function latLonIndex(model, lat, lon) {
    const cr = (model && model.crop) || [0, 0, 0, 0];
    if (!model || model.grid !== "lcc") {
      const res = model && /0\.1|9 km/.test(String(model.res || "")) ? 0.1 : 0.25;
      const fi = (90 - lat) / res - cr[0];
      const lon360 = ((lon % 360) + 360) % 360;
      return [fi, lon360 / res - cr[2]];
    }
    if (model.id && model.id !== "hrrr" && model.id !== "rrfs") return null;
    const o = lambertXY(HRRR_LCC.lon00, HRRR_LCC.lat00, HRRR_LCC);
    const q = lambertXY(lon, lat, HRRR_LCC);
    return [(q[1] - o[1]) / HRRR_LCC.dx - cr[0], (q[0] - o[0]) / HRRR_LCC.dx - cr[2]];
  }

  function kmToCoast(lat, lon, pts) {
    let best = 1e9;
    const clat = Math.max(Math.cos(lat * Math.PI / 180), 0.2);
    for (let i = 0; i < pts.length; i++) {
      const dlat = (lat - pts[i][1]) * 111.2, dlon = (lon - pts[i][0]) * 111.2 * clat;
      const d = Math.hypot(dlat, dlon);
      if (d < best) best = d;
    }
    return best;
  }
  function isCoastal(lat, lon, pts, km) {
    return kmToCoast(lat, lon, pts) <= (km == null ? 10 : km);
  }
  function isWaveProduct(pid) {
    return /^(waves|wavemax|wavemax24|swper|swellhs)$/.test(pid || "");
  }
  // The baked town picture includes inland cities. Wave maps on a lat/lon grid never draw it.
  function showStaticTowns(pid, grid) {
    return !(isWaveProduct(pid) && grid === "ll");
  }
  // Wave maps draw a town only when it sits on or within about 10 km of the coast, including Hawaii.
  function coastalTowns(towns, pts, km) {
    return (towns || []).filter(t => Number.isFinite(t.lat) && Number.isFinite(t.lon) && isCoastal(t.lat, t.lon, pts, km));
  }
  function decodeCoast(b64) {
    const raw = typeof atob === "function" ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
    const n = (raw.length / 4) | 0, pts = new Array(n);
    for (let i = 0; i < n; i++) {
      const o = i * 4;
      let lon = raw.charCodeAt(o) | (raw.charCodeAt(o + 1) << 8);
      let lat = raw.charCodeAt(o + 2) | (raw.charCodeAt(o + 3) << 8);
      if (lon & 0x8000) lon -= 0x10000;
      if (lat & 0x8000) lat -= 0x10000;
      pts[i] = [lon / 100, lat / 100];
    }
    return pts;
  }
  let _coast = null;
  function coastPoints() {
    if (_coast) return _coast;
    const b64 = typeof WXCoastB64 === "string" ? WXCoastB64 : "";
    _coast = b64 ? decodeCoast(b64) : [];
    return _coast;
  }

  // Valid time under the map. America/Los_Angeles so the hour is PST or PDT, labeled PT.
  // "Valid Fri 11-6 · 2 PM PT" (minutes only when the valid time is not on the hour).
  function formatValidPT(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "";
    const tz = "America/Los_Angeles";
    const part = opt => new Intl.DateTimeFormat("en-US", Object.assign({ timeZone: tz }, opt)).format(d);
    const wd = part({ weekday: "short" });
    const md = part({ month: "numeric", day: "numeric" }).split("/");
    let hm = part({ hour: "numeric", minute: "2-digit", hour12: true }).replace(/\s/g, " ");
    if (hm.indexOf(":00") >= 0) hm = hm.replace(":00", "");
    return "Valid " + wd + " " + md[0] + "-" + md[1] + " \u00b7 " + hm + " PT";
  }

  return { lookupKey, climParts, resolveSelection, publicName, formatValidPT, WA_PASSES, CA_PASSES, passUnit, formatPassValue, passCaption,
    passesForView, latLonIndex, kmToCoast, isCoastal, isWaveProduct, showStaticTowns, coastalTowns, decodeCoast, coastPoints };
});
