# Bekannte Defekte (BUGS.md)

Defekte, die beim Bug-Sweep identifiziert, aber nicht im laufenden Sweep behoben wurden.
Format: `[Status] Titel — Kurzbeschreibung`

---

## Offen

_(Keine offenen Bugs)_

---

## Behoben

### B-001: Modell-Auswahl nicht funktional
**Status:** Behoben (2026-06-05)  
**Datei:** `src/gui/main_window.py` — `_apply_settings()`  
**Fix:** `_apply_settings()` liest nun `ai.model` und ruft `set_model()` mit dem korrekten `AIModel`-Enum-Wert auf. Auch `max_tokens` wird übertragen.

### B-002: Rotes Validierungs-Rahmen in NewProjectDialog wird nicht zurückgesetzt
**Status:** Behoben (2026-06-05)  
**Datei:** `src/gui/dialogs/new_project_dialog.py` — `_reset_name_style()`  
**Fix:** `name_edit.textChanged` ist nun mit `_reset_name_style()` verbunden, das `setStyleSheet("")` aufruft und so den roten Rahmen beim nächsten Tastendruck löscht.

---

_Zuletzt aktualisiert: 2026-06-05 (Bug-Sweep Session)_
