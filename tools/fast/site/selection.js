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
    pnwhr: "pnw", pnwt: "pnw", pnw: "na", pac: "na",
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

  return { lookupKey, climParts, resolveSelection, publicName };
});
