import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  countChecklistProgress,
  formatExportDate,
  groupProblemsBySeverity,
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

// ── countChecklistProgress ──

test("countChecklistProgress: leere Liste ergibt 0/0/0%", () => {
  const result = countChecklistProgress([]);
  assert.deepEqual(result, { done: 0, total: 0, percent: 0 });
});

test("countChecklistProgress: kein Eintrag erledigt → 0%", () => {
  const checklists = [
    { title: "A", status: "open" },
    { title: "B", status: "open" },
  ];
  const result = countChecklistProgress(checklists);
  assert.deepEqual(result, { done: 0, total: 2, percent: 0 });
});

test("countChecklistProgress: alle erledigt → 100%", () => {
  const checklists = [
    { title: "A", status: "done" },
    { title: "B", status: "closed" },
  ];
  const result = countChecklistProgress(checklists);
  assert.deepEqual(result, { done: 2, total: 2, percent: 100 });
});

test("countChecklistProgress: halb erledigt → 50%", () => {
  const checklists = [
    { title: "A", status: "done" },
    { title: "B", status: "open" },
  ];
  const result = countChecklistProgress(checklists);
  assert.deepEqual(result, { done: 1, total: 2, percent: 50 });
});

test("countChecklistProgress: Demo-Fixture hat 0 erledigte von 2", () => {
  const result = countChecklistProgress(fixture.release.checklists);
  assert.equal(result.total, 2);
  assert.equal(result.done, 0);
  assert.equal(result.percent, 0);
});

test("countChecklistProgress: null/undefined wird wie leere Liste behandelt", () => {
  assert.deepEqual(countChecklistProgress(null), { done: 0, total: 0, percent: 0 });
  assert.deepEqual(countChecklistProgress(undefined), { done: 0, total: 0, percent: 0 });
});

// ── groupProblemsBySeverity ──

test("groupProblemsBySeverity: leere Liste ergibt leeres Array", () => {
  const groups = groupProblemsBySeverity([]);
  assert.deepEqual(groups, []);
});

test("groupProblemsBySeverity: sortiert error vor warning vor info", () => {
  const problems = [
    { severity: "info", message: "Info-Hinweis" },
    { severity: "warning", message: "Warnung" },
    { severity: "error", message: "Fehler" },
  ];
  const groups = groupProblemsBySeverity(problems);
  assert.deepEqual(
    groups.map((g) => g.severity),
    ["error", "warning", "info"],
  );
});

test("groupProblemsBySeverity: gleicher Schweregrad wird zusammengefasst", () => {
  const problems = [
    { severity: "warning", message: "W1" },
    { severity: "warning", message: "W2" },
  ];
  const groups = groupProblemsBySeverity(problems);
  assert.equal(groups.length, 1);
  assert.equal(groups[0].severity, "warning");
  assert.equal(groups[0].items.length, 2);
});

test("groupProblemsBySeverity: Demo-Fixture hat 1 warning und 1 error", () => {
  const groups = groupProblemsBySeverity(fixture.analysis.problems);
  const byKey = new Map(groups.map((g) => [g.severity, g.items.length]));
  assert.equal(byKey.get("error"), 1);
  assert.equal(byKey.get("warning"), 1);
});

test("groupProblemsBySeverity: Befund ohne severity wird als 'info' eingruppiert", () => {
  const problems = [{ message: "Unbekannt" }];
  const groups = groupProblemsBySeverity(problems);
  assert.equal(groups[0].severity, "info");
});

test("groupProblemsBySeverity: null/undefined wird wie leere Liste behandelt", () => {
  assert.deepEqual(groupProblemsBySeverity(null), []);
  assert.deepEqual(groupProblemsBySeverity(undefined), []);
});
