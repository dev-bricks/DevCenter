import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  formatExportDate,
  groupTasksByPriority,
  parseWorkspaceText,
  summarizeWorkspace,
} from "../library.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(__dirname, "..", "fixtures", "demo-workspace.json");
const fixtureText = fs.readFileSync(fixturePath, "utf8");
const fixture = JSON.parse(fixtureText);

test("parseWorkspaceText akzeptiert gültige DevCenter-Exporte", () => {
  const payload = parseWorkspaceText(fixtureText);
  assert.equal(payload.schema, "devcenter-workspace-v1");
  assert.equal(payload.project.name, "InvoiceTools");
});

test("parseWorkspaceText lehnt falsches Schema ab", () => {
  assert.throws(
    () => parseWorkspaceText(JSON.stringify({ schema: "other-schema", app: {}, project: {} })),
    /Unerwartetes Schema/,
  );
});

test("summarizeWorkspace liefert konsistente Kennzahlen", () => {
  const cards = summarizeWorkspace(fixture);
  const byLabel = new Map(cards.map((card) => [card.label, card.value]));
  assert.equal(byLabel.get("Dateien erfasst"), 37);
  assert.equal(byLabel.get("Probleme"), 2);
  assert.equal(byLabel.get("Offene Aufgaben"), 3);
});

test("groupTasksByPriority sortiert P-Gruppen vor sonstigen Gruppen", () => {
  const groups = groupTasksByPriority(fixture.tasks);
  assert.deepEqual(groups.map((group) => group.priority), ["P1", "P2", "Ohne Priorität"]);
});

test("formatExportDate gibt lesbaren Zeittext zurück", () => {
  const formatted = formatExportDate("2026-06-06T14:00:00Z");
  assert.match(formatted, /2026/);
});
