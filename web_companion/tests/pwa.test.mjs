import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const manifestPath = path.join(root, "manifest.webmanifest");
const swPath = path.join(root, "sw.js");
const indexPath = path.join(root, "index.html");
const appJsPath = path.join(root, "app.js");

// --- Manifest ---

test("manifest: display ist standalone", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.equal(m.display, "standalone");
});

test("manifest: start_url vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.equal(m.start_url, "./index.html");
});

test("manifest: id-Feld vorhanden (PWA-Installierbarkeit)", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(typeof m.id === "string" && m.id.length > 0, "id fehlt oder leer");
});

test("manifest: scope-Feld vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(typeof m.scope === "string" && m.scope.length > 0, "scope fehlt oder leer");
});

test("manifest: name und short_name vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(m.name && m.short_name);
});

test("manifest: SVG-Icon mit purpose any vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(Array.isArray(m.icons));
  assert.ok(m.icons.some((i) => i.src.endsWith("app.svg") && i.purpose === "any"));
});

test("manifest: maskable Icon vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(m.icons.some((i) => i.purpose === "maskable"));
});

test("manifest: Icon-SVG-Dateien physisch vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  for (const icon of m.icons) {
    const iconPath = path.join(root, icon.src.replace(/^\.\//, ""));
    assert.ok(fs.existsSync(iconPath), `Icon fehlt: ${icon.src}`);
  }
});

// --- Service Worker ---

test("sw.js: CACHE_NAME enthält 'devcenter'", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /devcenter/);
});

test("sw.js: CACHE_NAME ist v2 (aktuell)", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /devcenter-companion-v2/);
});

test("sw.js: skipWaiting() im install-Handler", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /self\.skipWaiting\(\)/);
});

test("sw.js: clients.claim() im activate-Handler", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /self\.clients\.claim\(\)/);
});

test("sw.js: Demo-Export und Shell-Dateien gecacht", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /demo-workspace\.json/);
  assert.match(src, /manifest\.webmanifest/);
  assert.match(src, /cache\.addAll/);
});

// --- HTML-Integration ---

test("index.html: verweist auf manifest.webmanifest", () => {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.match(html, /manifest\.webmanifest/);
});

test("app.js: registriert Service Worker", () => {
  const src = fs.readFileSync(appJsPath, "utf8");
  assert.match(src, /serviceWorker\.register/);
});

// --- Bug-Fix-Assertions ---

test("sw.js: caches.match setzt ignoreSearch:true (Offline-Fallback bei ?-Params)", () => {
  const src = fs.readFileSync(swPath, "utf8");
  assert.match(src, /ignoreSearch:\s*true/, "caches.match muss ignoreSearch:true setzen – offline schlägt bei ?demo=1 fehl");
});

test("index.html: apple-touch-icon vorhanden (iOS Homescreen-Icon)", () => {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.match(html, /rel="apple-touch-icon"/, "apple-touch-icon fehlt – iOS zeigt generischen Screenshot");
});

test("manifest: lang-Feld vorhanden", () => {
  const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.ok(m.lang, "lang fehlt im Manifest");
});

test("app.js: fileInput-Handler fängt file.text()-Fehler ab", () => {
  const src = fs.readFileSync(appJsPath, "utf8");
  assert.match(src, /file\.text\(\)/, "file.text() muss vorhanden sein");
  assert.match(src, /Datei konnte nicht gelesen werden/, "Fehlerfall für file.text() fehlt");
});

test("app.js: deferredInstallPrompt wird vor prompt() genullt", () => {
  const src = fs.readFileSync(appJsPath, "utf8");
  assert.match(src, /deferredInstallPrompt\s*=\s*null/, "deferredInstallPrompt muss nach prompt() genullt werden");
});
