import {
  countChecklistProgress,
  formatExportDate,
  groupProblemsBySeverity,
  groupTasksByPriority,
  parseWorkspaceText,
  summarizeWorkspace,
  toArray,
} from "./library.js";

const STORAGE_KEY = "devcenter-web-companion:last-workspace";
const DEMO_PATH = "./fixtures/demo-workspace.json";

const elements = {
  installButton: document.querySelector("#install-button"),
  installStatus: document.querySelector("#install-status"),
  lastLoaded: document.querySelector("#last-loaded"),
  fileInput: document.querySelector("#file-input"),
  jsonInput: document.querySelector("#json-input"),
  pasteButton: document.querySelector("#paste-button"),
  demoButton: document.querySelector("#demo-button"),
  clearButton: document.querySelector("#clear-button"),
  message: document.querySelector("#message"),
  workspaceShell: document.querySelector("#workspace-shell"),
  projectKicker: document.querySelector("#project-kicker"),
  projectName: document.querySelector("#project-name"),
  projectMeta: document.querySelector("#project-meta"),
  frameworkChips: document.querySelector("#framework-chips"),
  summaryGrid: document.querySelector("#summary-grid"),
  analysisSummary: document.querySelector("#analysis-summary"),
  problemsList: document.querySelector("#problems-list"),
  buildDetails: document.querySelector("#build-details"),
  releaseTargets: document.querySelector("#release-targets"),
  releaseChecklists: document.querySelector("#release-checklists"),
  tasksGroups: document.querySelector("#tasks-groups"),
  dependenciesList: document.querySelector("#dependencies-list"),
  redactionsList: document.querySelector("#redactions-list"),
};

let deferredInstallPrompt = null;

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  elements.installButton.hidden = false;
  elements.installStatus.textContent = "Installierbar im Browser";
});

window.addEventListener("appinstalled", () => {
  deferredInstallPrompt = null;
  elements.installButton.hidden = true;
  elements.installStatus.textContent = "Als App installiert";
});

elements.installButton?.addEventListener("click", async () => {
  if (!deferredInstallPrompt) {
    return;
  }
  const prompt = deferredInstallPrompt;
  deferredInstallPrompt = null;
  prompt.prompt();
  await prompt.userChoice;
});

elements.fileInput?.addEventListener("change", async (event) => {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }
  let text;
  try {
    text = await file.text();
  } catch {
    setMessage("Datei konnte nicht gelesen werden.", "error");
    return;
  }
  loadWorkspace(text, `Datei: ${file.name}`);
});

elements.pasteButton?.addEventListener("click", () => {
  loadWorkspace(elements.jsonInput.value, "Manuelle Eingabe");
});

elements.demoButton?.addEventListener("click", async () => {
  const response = await fetch(DEMO_PATH);
  if (!response.ok) {
    setMessage("Demo-Datei konnte nicht geladen werden.", "error");
    return;
  }
  const text = await response.text();
  loadWorkspace(text, "Demo");
});

elements.clearButton?.addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  elements.workspaceShell.hidden = true;
  elements.jsonInput.value = "";
  elements.fileInput.value = "";
  elements.lastLoaded.textContent = "Noch kein Arbeitsstand geladen";
  setMessage("Gespeicherten Companion-Stand entfernt.", "info");
});

registerServiceWorker();
restoreWorkspace();
loadDemoFromQuery();

function loadWorkspace(text, sourceLabel) {
  try {
    const payload = parseWorkspaceText(text);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // QuotaExceededError (Safari Private / voller Speicher) — Anzeige trotzdem fortsetzen
    }
    renderWorkspace(payload, sourceLabel);
    setMessage(`Arbeitsstand geladen: ${sourceLabel}`, "success");
  } catch (error) {
    setMessage(error.message, "error");
  }
}

function renderWorkspace(payload, sourceLabel) {
  const summaryCards = summarizeWorkspace(payload);
  const frameworks = toArray(payload.project.frameworks);
  const problems = toArray(payload.analysis?.problems);
  const problemGroups = groupProblemsBySeverity(problems);
  const checklistProgress = countChecklistProgress(toArray(payload.release?.checklists));
  const tasks = groupTasksByPriority(payload.tasks);
  const requirements = toArray(payload.dependencies?.requirements);
  const releaseTargets = toArray(payload.release?.targets);
  const releaseChecklists = toArray(payload.release?.checklists);
  const redactions = Object.entries(payload.redactions || {});

  elements.workspaceShell.hidden = false;
  elements.projectKicker.textContent = sourceLabel || "Arbeitsstand";
  elements.projectName.textContent = payload.project.name || payload.app.name || "DevCenter";
  elements.projectMeta.textContent = [
    payload.project.description || "Redigierter Export für den Companion",
    `Export: ${formatExportDate(payload.app.exported_at)}`,
    payload.project.version ? `Version ${payload.project.version}` : null,
  ].filter(Boolean).join(" • ");
  elements.lastLoaded.textContent = formatExportDate(payload.app.exported_at);

  replaceChildren(
    elements.frameworkChips,
    frameworks.map((framework) => createChip(framework)),
  );

  replaceChildren(
    elements.summaryGrid,
    summaryCards.map((card) => {
      const article = document.createElement("article");
      article.className = `stat-card stat-card--${card.tone}`;

      const label = document.createElement("p");
      label.className = "stat-card__label";
      label.textContent = card.label;

      const value = document.createElement("p");
      value.className = "stat-card__value";
      value.textContent = String(card.value);

      article.append(label, value);
      return article;
    }),
  );

  replaceChildren(
    elements.analysisSummary,
    [
      createMetaLine("Projektpfad", payload.project.path_ref || "project-1"),
      createMetaLine("Hauptdatei", payload.project.main_file_ref || "nicht gesetzt"),
      createMetaLine("Sprache", payload.project.language || "python"),
    ],
  );

  replaceChildren(
    elements.problemsList,
    problemGroups.length
      ? problemGroups.flatMap(({ severity, items }) => {
          const groupHeader = document.createElement("li");
          groupHeader.className = "problem-group-header";
          const groupLabel = document.createElement("strong");
          groupLabel.textContent = severity.charAt(0).toUpperCase() + severity.slice(1);
          groupHeader.append(groupLabel);

          const problemItems = items.map((problem) => {
            const item = document.createElement("li");
            item.className = "problem-item";

            const title = document.createElement("strong");
            title.textContent = `${problem.code || "Befund"}`;

            const text = document.createElement("p");
            text.textContent = problem.message || "Ohne Text";

            const meta = document.createElement("p");
            meta.className = "muted";
            meta.textContent = [problem.file_ref, positionLabel(problem.line, problem.column), problem.source]
              .filter(Boolean)
              .join(" • ");

            item.append(title, text, meta);
            return item;
          });

          return [groupHeader, ...problemItems];
        })
      : [createEmptyItem("Keine exportierten Analyseprobleme vorhanden.")],
  );

  replaceChildren(
    elements.buildDetails,
    [
      createDetailRow("Ziel", payload.build?.target || "nicht gesetzt"),
      createDetailRow("Output", payload.build?.output_ref || "nicht gesetzt"),
      createDetailRow("One File", payload.build?.one_file ? "Ja" : "Nein"),
      createDetailRow("Console", payload.build?.console ? "Ja" : "Nein"),
      createDetailRow("Icon", payload.build?.icon_ref || "kein Icon exportiert"),
    ],
  );

  replaceChildren(
    elements.releaseTargets,
    releaseTargets.length
      ? releaseTargets.map((target) => createChip(target))
      : [createChip("Keine Targets exportiert")],
  );

  replaceChildren(
    elements.releaseChecklists,
    releaseChecklists.length
      ? [
          createChecklistProgressBar(checklistProgress),
          ...releaseChecklists.map((entry) => createListItem(entry.title, entry.status || "open")),
        ]
      : [createEmptyItem("Keine Release-Checklisten im Export enthalten.")],
  );

  replaceChildren(
    elements.tasksGroups,
    tasks.length
      ? tasks.map((group) => {
          const wrapper = document.createElement("section");
          wrapper.className = "stack stack--tight";

          const heading = document.createElement("h4");
          heading.className = "group-heading";
          heading.textContent = group.priority;

          const list = document.createElement("ul");
          list.className = "list";
          group.items.forEach((task) => {
            list.append(createListItem(task.title, task.section || "offen"));
          });

          wrapper.append(heading, list);
          return wrapper;
        })
      : [createMetaLine("Status", "Keine offenen Aufgaben exportiert.")],
  );

  replaceChildren(
    elements.dependenciesList,
    requirements.length
      ? requirements.map((entry) =>
          createListItem(entry.name, entry.specifier || "ohne Versionsgrenze"),
        )
      : [createEmptyItem("Keine Requirements im Export enthalten.")],
  );

  replaceChildren(
    elements.redactionsList,
    redactions.length
      ? redactions.map(([key, enabled]) =>
          createListItem(key, enabled ? "redigiert" : "nicht redigiert"),
        )
      : [createEmptyItem("Keine Redaktionshinweise vorhanden.")],
  );
}

function createChip(label) {
  const item = document.createElement("li");
  item.className = "chip";
  item.textContent = label;
  return item;
}

function createDetailRow(term, description) {
  const fragment = document.createDocumentFragment();
  const dt = document.createElement("dt");
  dt.textContent = term;
  const dd = document.createElement("dd");
  dd.textContent = description;
  fragment.append(dt, dd);
  return fragment;
}

function createListItem(title, meta) {
  const item = document.createElement("li");
  item.className = "list__item";

  const strong = document.createElement("strong");
  strong.textContent = title;

  const text = document.createElement("span");
  text.className = "muted";
  text.textContent = meta;

  item.append(strong, text);
  return item;
}

function createEmptyItem(message) {
  const item = document.createElement("li");
  item.className = "list__item list__item--empty";
  item.textContent = message;
  return item;
}

function createChecklistProgressBar({ done, total, percent }) {
  const wrapper = document.createElement("li");
  wrapper.className = "checklist-progress";

  const label = document.createElement("p");
  label.className = "muted";
  label.textContent = `${done} von ${total} erledigt`;

  const track = document.createElement("div");
  track.className = "progress-track";

  const fill = document.createElement("div");
  fill.className = "progress-fill";
  fill.style.width = `${percent}%`;
  fill.setAttribute("role", "progressbar");
  fill.setAttribute("aria-valuenow", String(percent));
  fill.setAttribute("aria-valuemin", "0");
  fill.setAttribute("aria-valuemax", "100");

  track.append(fill);
  wrapper.append(label, track);
  return wrapper;
}

function createMetaLine(label, value) {
  const wrapper = document.createElement("p");
  wrapper.className = "meta-line";
  wrapper.innerHTML = `<strong>${escapeHtml(label)}:</strong> ${escapeHtml(value)}`;
  return wrapper;
}

function replaceChildren(node, children) {
  node.replaceChildren(...children);
}

function setMessage(text, type) {
  elements.message.textContent = text;
  elements.message.dataset.type = type;
}

function positionLabel(line, column) {
  if (!line) {
    return "";
  }
  if (!column) {
    return `Zeile ${line}`;
  }
  return `Zeile ${line}, Spalte ${column}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    elements.installStatus.textContent = "PWA-Shell ohne Service Worker";
    return;
  }
  navigator.serviceWorker.register("./sw.js").then(() => {
    if (!deferredInstallPrompt) {
      elements.installStatus.textContent = "Offline-Shell aktiv";
    }
  }).catch(() => {
    elements.installStatus.textContent = "Service Worker konnte nicht registriert werden";
  });
}

function restoreWorkspace() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }
  loadWorkspace(raw, "Lokaler Cache");
}

function loadDemoFromQuery() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("demo") !== "1") {
    return;
  }
  elements.demoButton?.click();
}
