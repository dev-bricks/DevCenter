import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const manifestPath = path.join(__dirname, "..", "manifest.webmanifest");
const swPath = path.join(__dirname, "..", "sw.js");

test("manifest definiert standalone-PWA mit SVG-Icons", () => {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.equal(manifest.display, "standalone");
  assert.equal(manifest.start_url, "./index.html");
  assert.ok(Array.isArray(manifest.icons));
  assert.ok(manifest.icons.some((icon) => icon.src.endsWith("app.svg")));
});

test("service worker cached den Demo-Export und die Shell-Dateien", () => {
  const source = fs.readFileSync(swPath, "utf8");
  assert.match(source, /demo-workspace\.json/);
  assert.match(source, /manifest\.webmanifest/);
  assert.match(source, /cache\.addAll/);
});
