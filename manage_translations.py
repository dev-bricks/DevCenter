"""
manage_translations.py - Auto-Scanner für GUI-Strings (Tier-2 Mehrsprachigkeit)
================================================================================
Findet GUI-Strings in .py-Dateien und pflegt locales/translations.json für
alle 6 unterstützten Sprachen: DE, EN, ES, ZH, JA, RU (gemäß P-006).

Verwendung:
    python manage_translations.py [--dir PROJEKTVERZEICHNIS]
"""

import json
import re
import os
import sys

TRANSLATION_FILE = "locales/translations.json"
SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setToolTip\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setStatusTip\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren", "wählen",
    "erfolgreich", "hinweis", "warnung", "ausgabeordner", "ausführen",
    "projekt", "erklären", "erstellen", "suchen", "ersetzen",
]


def is_german(text: str) -> bool:
    """Prüft, ob ein String deutschen Text enthält."""
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir: str) -> set:
    """Scannt Quelltextdateien nach GUI-Strings."""
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def manage_translations(source_dir: str = "."):
    """Aktualisiert translations.json mit neu gefundenen Strings."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {lang: (s if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
            added.append(s)

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)

    if added:
        print(f"[+] {len(added)} neue Einträge hinzugefügt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")
    for lang in SUPPORTED_LANGUAGES:
        missing = [k for k, v in translations.items() if not v.get(lang)]
        if missing:
            print(f"    - {lang.upper()}: {len(missing)} fehlende Übersetzungen")
        else:
            print(f"    - {lang.upper()}: 100% vollständig")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    manage_translations(target)
