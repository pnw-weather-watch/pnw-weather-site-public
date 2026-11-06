"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const { lookupKey, climParts, resolveSelection, publicName, formatPassValue, passCaption, passesForView,
  WA_PASSES, CA_PASSES, latLonIndex, showStaticTowns, coastalTowns, isWaveProduct, decodeCoast } = require("./selection.js");

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
  assert.match(r.note, /That product isn't in this run/);
  assert.match(r.note, /Showing 2 m Temperature/);
  assert.doesNotMatch(r.note, /no-such-product/);
  assert.doesNotMatch(r.note, /Big Island/);
});

test("unknown view falls back to Pacific Northwest with no overlay", () => {
  const r = resolve("t2ma", "not-a-view");
  assert.equal(r.prod, "t2ma");
  assert.equal(r.view, "pnw");
  assert.equal(r.note, null);
  assert.equal(r.prefer, "not-a-view");
  assert.notEqual(r.view, "bigi");
});

test("high-res Pacific Northwest falls back to Pacific Northwest with no raw id", () => {
  const r = resolve("t2m", "pnwhr", { prodTitle: "2 m Temperature (ens. mean)" });
  assert.equal(r.view, "pnw");
  assert.equal(r.note, null);
  assert.equal(r.prefer, "pnwhr");
});

test("switching back to a model that has the view restores it", () => {
  const away = resolve("t2m", "pnwhr", { prodTitle: "2 m Temperature (ens. mean)" });
  assert.equal(away.view, "pnw");
  const hrrr = [
    ["pnwhr", "Pacific NW (high-res)"], ["passes", "Cascade Passes"], ["ca", "California"],
  ].map(([id, label]) => ({ id, label, waveOnly: false }));
  const back = resolve("t2m", away.prefer, { views: hrrr, prodTitle: "2 m Temperature" });
  assert.equal(back.view, "pnwhr");
  assert.equal(back.note, null);
});

test("both product and view unsupported stay silent about the view and hide raw ids", () => {
  const r = resolve("retired", "retired-view", { prodTitle: "retired" });
  assert.equal(r.prod, "t2m");
  assert.equal(r.view, "pnw");
  assert.match(r.note, /That product isn't in this run/);
  assert.doesNotMatch(r.note, /isn't a view/);
  assert.doesNotMatch(r.note, /retired/);
  assert.equal(publicName("pnwhr", "Map"), "Map");
  assert.equal(publicName("Pacific Northwest", "Map"), "Pacific Northwest");
});

test("wave-only view with a temperature product falls back and says why", () => {
  const views = ensViews.concat([{ id: "wc", label: "West Coast", waveOnly: true }]);
  const r = resolve("t2m", "wc", { views, prodTitle: "2 m Temperature (ens. mean)" });
  assert.equal(r.prod, "t2m");
  assert.equal(r.view, "pnw");
  assert.match(r.note, /West Coast is only for wave maps/);
  assert.doesNotMatch(r.note, /\bwc\b/);
  const raw = resolve("t2m", "wc", { views: ensViews.concat([{ id: "wc", label: "wc", waveOnly: true }]), prodTitle: "2 m Temperature (ens. mean)" });
  assert.match(raw.note, /That view is only for wave maps/);
  assert.doesNotMatch(raw.note, /\bwc\b/);
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

test("pass labels carry units and skip imagery products", () => {
  assert.equal(passCaption("Snoqualmie", formatPassValue("t2m", {}, 31.2)), "Snoqualmie 31\u00b0F");
  assert.equal(passCaption("Stevens", formatPassValue("snow", { fmt: "in1" }, 6.24)), "Stevens 6.2\"");
  assert.equal(passCaption("White", formatPassValue("gust10", {}, 45.2)), "White 45 mph");
  assert.equal(formatPassValue("refc", {}, 35), null);
  assert.equal(formatPassValue("ir", {}, -40), null);
  assert.equal(formatPassValue("ptype", {}, 3), null);
  assert.equal(formatPassValue("spag", {}, 5400), null);
  assert.equal(passCaption("Chinook", null), "Chinook");
  assert.equal(passesForView("passes").length, 9);
  assert.equal(passesForView("passes")[0].id, "Snoqualmie Pass");
  assert.equal(passesForView("capasses").find(p => p.label === "Black Butte").elev, 3912);
  assert.equal(passesForView("pnw").length, 0);
  assert.equal(WA_PASSES.length, 9);
  assert.equal(CA_PASSES.length, 13);
});

test("HRRR Lambert index lands on Snoqualmie", () => {
  const [fi, fj] = latLonIndex({ id: "hrrr", grid: "lcc" }, 47.4245, -121.4136);
  assert.ok(Math.abs(fi - 939.754) < 0.02, String(fi));
  assert.ok(Math.abs(fj - 298.598) < 0.02, String(fj));
  const gfs = latLonIndex({ id: "gfs", grid: "ll", crop: [0, 0, 0, 0] }, 47.4245, -121.4136);
  assert.ok(gfs[0] > 160 && gfs[0] < 180);
});

test("wave products never keep inland towns", () => {
  assert.equal(isWaveProduct("waves"), true);
  assert.equal(isWaveProduct("swper"), true);
  assert.equal(isWaveProduct("t2m"), false);
  assert.equal(showStaticTowns("waves", "ll"), false);
  assert.equal(showStaticTowns("wavemax", "ll"), false);
  assert.equal(showStaticTowns("swellhs", "ll"), false);
  assert.equal(showStaticTowns("t2m", "ll"), true);
  const src = fs.readFileSync(path.join(__dirname, "coastline.js"), "utf8");
  const pts = decodeCoast(src.match(/"([A-Za-z0-9+/=]+)"/)[1]);
  const towns = [
    { name: "Spokane", lat: 47.6588, lon: -117.426 },
    { name: "Sacramento", lat: 38.58, lon: -121.49 },
    { name: "Denver", lat: 39.74, lon: -104.99 },
    { name: "Wahiawa", lat: 21.503, lon: -158.025 },
    { name: "Seattle", lat: 47.6062, lon: -122.3321 },
    { name: "Westport", lat: 46.89, lon: -124.104 },
    { name: "Hilo", lat: 19.73, lon: -155.09 },
    { name: "Honolulu", lat: 21.307, lon: -157.858 },
    { name: "Kailua-Kona", lat: 19.64, lon: -155.996 },
  ];
  const keep = new Set(coastalTowns(towns, pts).map(t => t.name));
  for (const inland of ["Spokane", "Sacramento", "Denver", "Wahiawa"]) assert.equal(keep.has(inland), false, inland);
  for (const shore of ["Seattle", "Westport", "Hilo", "Honolulu", "Kailua-Kona"]) assert.equal(keep.has(shore), true, shore);
});
