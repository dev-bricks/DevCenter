export const SCHEMA_NAME = "devcenter-workspace-v1";

export function parseWorkspaceText(text) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch (error) {
    throw new Error("Die JSON-Datei ist nicht gültig.");
  }

  validateWorkspace(payload);
  return payload;
}

export function validateWorkspace(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Der Export muss ein JSON-Objekt sein.");
  }

  if (payload.schema !== SCHEMA_NAME) {
    throw new Error("Unerwartetes Schema. Erwartet wird devcenter-workspace-v1.");
  }

  if (!payload.app || !payload.project) {
    throw new Error("Pflichtbereiche app und project fehlen.");
  }
}

export function summarizeWorkspace(payload) {
  const analysis = payload.analysis ?? {};
  const summary = analysis.summary ?? {};
  const tasks = toArray(payload.tasks);
  const release = payload.release ?? {};
  const dependencies = payload.dependencies ?? {};

  return [
    {
      label: "Dateien erfasst",
      value: numberValue(summary.files_indexed),
      tone: "neutral",
    },
    {
      label: "Probleme",
      value: numberValue(summary.problems_total),
      tone: numberValue(summary.problems_total) > 0 ? "alert" : "good",
    },
    {
      label: "Warnungen",
      value: numberValue(summary.warnings_total),
      tone: numberValue(summary.warnings_total) > 0 ? "warn" : "good",
    },
    {
      label: "Offene Aufgaben",
      value: tasks.length,
      tone: tasks.length > 0 ? "neutral" : "good",
    },
    {
      label: "Release-Checks",
      value: toArray(release.checklists).length,
      tone: "neutral",
    },
    {
      label: "Dependencies",
      value: toArray(dependencies.requirements).length,
      tone: "neutral",
    },
  ];
}

export function groupTasksByPriority(tasks) {
  const groups = new Map();
  for (const task of toArray(tasks)) {
    const key = task.priority || "Ohne Priorität";
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key).push(task);
  }

  return [...groups.entries()].sort(comparePriorityGroups).map(([priority, items]) => ({
    priority,
    items,
  }));
}

export function formatExportDate(value) {
  if (!value) {
    return "ohne Zeitstempel";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function toArray(value) {
  return Array.isArray(value) ? value : [];
}

/**
 * Berechnet den Erledigungsfortschritt einer Checkliste.
 * Gibt die Anzahl erledigter Einträge, die Gesamtzahl und den Prozentwert (0–100) zurück.
 * @param {Array} checklists
 * @returns {{ done: number, total: number, percent: number }}
 */
export function countChecklistProgress(checklists) {
  const items = toArray(checklists);
  const done = items.filter((item) => item.status === "done" || item.status === "closed").length;
  return {
    done,
    total: items.length,
    percent: items.length > 0 ? Math.round((done / items.length) * 100) : 0,
  };
}

const SEVERITY_RANK = { error: 0, warning: 1, info: 2 };

/**
 * Gruppiert Analysebefunde nach Schweregrad.
 * Rückgabe: Array von { severity, items }, sortiert nach Rank (error → warning → info → sonstige).
 * @param {Array} problems
 * @returns {Array<{ severity: string, items: Array }>}
 */
export function groupProblemsBySeverity(problems) {
  const groups = new Map();
  for (const problem of toArray(problems)) {
    const key = problem.severity || "info";
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key).push(problem);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => {
      const rankA = SEVERITY_RANK[a] ?? 99;
      const rankB = SEVERITY_RANK[b] ?? 99;
      if (rankA !== rankB) {
        return rankA - rankB;
      }
      return a.localeCompare(b, "de");
    })
    .map(([severity, items]) => ({ severity, items }));
}

function numberValue(value) {
  return Number.isFinite(Number(value)) ? Number(value) : 0;
}

function comparePriorityGroups(a, b) {
  const rankA = priorityRank(a[0]);
  const rankB = priorityRank(b[0]);
  if (rankA !== rankB) {
    return rankA - rankB;
  }
  return String(a[0]).localeCompare(String(b[0]), "de");
}

function priorityRank(priority) {
  const match = /^P(\d+)$/i.exec(String(priority));
  return match ? Number(match[1]) : 99;
}
