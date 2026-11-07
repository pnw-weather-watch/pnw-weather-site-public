import assert from "node:assert/strict";
import test from "node:test";
import { dataPrefix } from "./functions/d/[[path]].js";

test("production reads the live keys even when a prefix is set", () => {
  assert.equal(dataPrefix("pnw-weather-site.pages.dev", { WX_DATA_PREFIX: "preview-pr16" }), "");
  assert.equal(dataPrefix("pnw-weather-site.pages.dev", {}), "");
});

test("the PR alias maps to its own prefix", () => {
  assert.equal(dataPrefix("preview-pr16.pnw-weather-site.pages.dev", {}), "preview-pr16/");
  assert.equal(dataPrefix("preview-pr19.pnw-weather-site.pages.dev", {}), "preview-pr19/");
});

test("WX_DATA_PREFIX overrides the alias and the shared preview", () => {
  assert.equal(dataPrefix("preview-pr16.pnw-weather-site.pages.dev", { WX_DATA_PREFIX: "preview-crop" }), "preview-crop/");
  assert.equal(dataPrefix("preview.pnw-weather-site.pages.dev", { WX_DATA_PREFIX: "preview-pr16/" }), "preview-pr16/");
});

test("other hosts keep the shared preview prefix", () => {
  assert.equal(dataPrefix("preview.pnw-weather-site.pages.dev", {}), "preview/");
  assert.equal(dataPrefix("fast.pnw-weather-site.pages.dev", {}), "preview/");
  assert.equal(dataPrefix("cursor-pnwwide.pnw-weather-site.pages.dev", {}), "preview/");
});

test("a prefix that is not a preview area is ignored", () => {
  assert.equal(dataPrefix("preview-pr16.pnw-weather-site.pages.dev", { WX_DATA_PREFIX: "../live" }), "preview-pr16/");
  assert.equal(dataPrefix("other.example", { WX_DATA_PREFIX: "runs/" }), "preview/");
});
