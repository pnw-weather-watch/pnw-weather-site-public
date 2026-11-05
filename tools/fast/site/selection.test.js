"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { lookupKey, climParts, resolveSelection } = require("./selection.js");

const ensViews = [
  ["na", "North America"], ["pac", "Pacific"], ["pnw", "Pacific Northwest"],
  ["pnwt", "Pacific NW tight"], ["ca", "California"], ["socal", "Southern California"],
  ["cenca", "Central California"], ["norca", "Northern California"], ["bay", "SF Bay"],
  ["orco", "Oregon Coast"], ["hiw", "Hawaii"], ["bigi", "Big Island"],
].map(([id, label]) => ({ id, label, waveOnly: false }));
const ensProducts = [
  { id: "t2m", title: "2 m Temperature (ens. mean)", tab: "sfc" },
  { id: "t2ma", title: "2 m Temperature Anomaly (ens. mean)", tab: "sfc" },
];
const tabOf = pid => ({ t2m: "sfc", t2ma: "sfc", feels: "sfc", waves: "wav" }[pid] || "other");
const isWave = id => /^(waves|wavemax|wavemax24|swper|swellhs)$/.test(id);

function resolve(prod, view, extra) {
  return resolveSelection(Object.assign({
    products: ensProducts, views: ensViews, prod, view, tabOf, isWave,
    prodTitle: prod === "t2ma" ? "2 m Temperature Anomaly (ens. mean)" : prod,
  }, extra || {}));
}

test("EPS and AIFS ensemble temperature anomaly keep North America", () => {
  for (const model of ["eps", "aens"]) {
    const r = resolve("t2ma", "na");
    assert.equal(r.prod, "t2ma", model);
    assert.equal(r.view, "na", model);
    assert.equal(r.note, null, model);
    assert.equal(r.changed, false, model);
  }
});

test("a supported product keeps North America when another view was previously open", () => {
  const r = resolve("t2ma", "na");
  assert.notEqual(r.view, "bigi");
  assert.equal(r.view, "na");
});

test("unknown product falls back inside the same tab and keeps a valid view", () => {
  const r = resolve("no-such-product", "na", { prodTitle: "no-such-product", currentTab: "sfc" });
  assert.equal(r.prod, "t2m");
  assert.equal(r.view, "na");
  assert.match(r.note, /isn't in this run/);
  assert.match(r.note, /Showing 2 m Temperature/);
  assert.doesNotMatch(r.note, /Big Island/);
});

test("unknown view falls back to Pacific Northwest and keeps the anomaly product", () => {
  const r = resolve("t2ma", "not-a-view");
  assert.equal(r.prod, "t2ma");
  assert.equal(r.view, "pnw");
  assert.match(r.note, /isn't a view on this model/);
  assert.match(r.note, /Pacific Northwest/);
  assert.notEqual(r.view, "bigi");
});

test("both product and view unsupported use the same fallback, not the previous Big Island map", () => {
  const r = resolve("retired", "retired-view", { prodTitle: "retired" });
  assert.equal(r.prod, "t2m");
  assert.equal(r.view, "pnw");
  assert.match(r.note, /isn't in this run/);
  assert.match(r.note, /isn't a view on this model/);
});

test("wave-only view with a temperature product falls back and says why", () => {
  const views = ensViews.concat([{ id: "wc", label: "West Coast", waveOnly: true }]);
  const r = resolve("t2m", "wc", { views, prodTitle: "2 m Temperature (ens. mean)" });
  assert.equal(r.prod, "t2m");
  assert.equal(r.view, "pnw");
  assert.match(r.note, /only for wave maps/);
});

test("wave product keeps a wave-only view", () => {
  const views = ensViews.concat([{ id: "wc", label: "West Coast", waveOnly: true }]);
  const products = ensProducts.concat([{ id: "waves", title: "Wave height", tab: "wav" }]);
  const r = resolve("waves", "wc", { views, products, prodTitle: "Wave height" });
  assert.equal(r.prod, "waves");
  assert.equal(r.view, "wc");
  assert.equal(r.note, null);
});

test("model without Pacific Northwest uses the high-res view, then the first view", () => {
  const views = [{ id: "pnwhr", label: "PNW", waveOnly: false }, { id: "passes", label: "Passes", waveOnly: false }];
  const r = resolve("t2ma", "na", { views });
  assert.equal(r.view, "pnwhr");
  const only = [{ id: "bigi", label: "Big Island", waveOnly: false }];
  assert.equal(resolve("t2ma", "na", { views: only }).view, "bigi");
});

test("anomaly key lookup does not throw when the manifest has no key for North America", () => {
  const product = { keys: {} };
  assert.equal(lookupKey(product, { label: "North America" }, "na", "t2ma"), null);
  assert.equal(lookupKey({ keys: { na: "static/key_eps_t2ma_na.png" } }, {}, "na", "t2ma"), "static/key_eps_t2ma_na.png");
  assert.equal(lookupKey({ keys: { pnw: "static/key_eps_t2ma_pnw.png" } }, { src: "pnw" }, "na", "t2ma"), "static/key_eps_t2ma_pnw.png");
  assert.equal(lookupKey({ keys: { wa: "static/key_x.png" } }, { keysFrom: "wa" }, "na", "t2ma"), "static/key_x.png");
  assert.equal(lookupKey({ keys: { na: "static/from-product.png" } }, { keys: { t2ma: "static/from-view.png" } }, "na", "t2ma"), "static/from-view.png");
  assert.equal(lookupKey(null, {}, "na", "t2ma"), null);
});

test("climatology slots stay inside the file list (November 03Z uses hours 40 and 41)", () => {
  const clim = { hours: [0, 6, 12, 18], files: Array.from({ length: 48 }, (_, i) => `static/clim_${i}.png`), ranges: Array.from({ length: 48 }, () => [-50, 90]) };
  // 4 Nov 03Z is before mid-month, so October (36, 37) blends with November (40, 41), each across the 00Z and 06Z slots.
  const parts = climParts(clim, "2026-11-04T03:00:00+00:00");
  assert.deepEqual(parts.map(p => p[0]).sort((a, b) => a - b), [36, 37, 40, 41]);
  assert.ok(parts.every(p => p[1] > 0 && p[1] < 1));
  const short = climParts({ hours: [0, 6, 12, 18], files: ["a", "b", "c", "d"], ranges: [[0, 1], [0, 1], [0, 1], [0, 1]] }, "2026-11-04T03:00:00+00:00");
  assert.deepEqual(short, []);
  assert.equal(climParts(null, "2026-11-04T03:00:00+00:00"), null);
  assert.deepEqual(climParts(clim, "not-a-date"), []);
});
