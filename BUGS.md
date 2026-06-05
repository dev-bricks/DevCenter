# Bekannte Defekte (BUGS.md)

Defekte, die beim Bug-Sweep identifiziert, aber nicht im laufenden Sweep behoben wurden.
Format: `[Status] Titel — Kurzbeschreibung`

---

## Offen

### B-001: Modell-Auswahl nicht funktional
**Status:** Offen  
**Datei:** `src/gui/main_window.py` — `_apply_settings()`  
**Schwere:** Mittel (Feature silent broken)  
**Beschreibung:**  
`_apply_settings()` liest `ai.model` aus den Einstellungen, ruft aber `ai_service.set_model()` nie auf. Der gespeicherte Wert ist zudem der Anzeigename (z. B. "Claude Haiku") statt der API-ID. Die Modell-Auswahl in den Einstellungen wird daher vollständig ignoriert.  
**Workaround:** Keiner. Das KI-Modell bleibt beim Standardwert der `AIService`-Instanz.

### B-002: Rotes Validierungs-Rahmen in NewProjectDialog wird nicht zurückgesetzt
**Status:** Offen  
**Datei:** `src/gui/dialogs/new_project_dialog.py` — `_validate_input()` / `name_edit`  
**Schwere:** Gering (kosmetischer UX-Defekt)  
**Beschreibung:**  
Wenn der Benutzer im `NewProjectDialog` einen ungültigen Projektnamen eingibt und auf "Erstellen" klickt, setzt `_validate_input()` einen roten Rahmen auf `name_edit`. Sobald der Benutzer dann wieder zu tippen beginnt, wird dieser Rahmen nicht automatisch zurückgesetzt. Der rote Rahmen bleibt, bis das Formular neu validiert wird.  
**Workaround:** Nutzer muss das Formular erneut absenden, um den Rahmen zu entfernen.

---

_Zuletzt aktualisiert: 2026-06-05 (Bug-Sweep Session)_
