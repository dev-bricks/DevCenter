# -*- coding: utf-8 -*-
"""
DevCenter - Python Development Suite
Haupteinstiegspunkt der Anwendung

Starten mit:
    python main.py
oder:
    python -m src.gui.main_window
"""

import sys
import os
import logging

# Pfad zum src-Verzeichnis hinzufügen
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from runtime.app_logging import start as start_logging

if __name__ == "__main__":
    start_logging(app_slug="DevCenter")
    logging.getLogger("DevCenter").info("Starte DevCenter aus %s", os.path.abspath(__file__))
    # Erst nach dem Logger importieren: auch Importfehler des GUI-Stacks landen
    # beim fensterlosen pythonw-Start zuverlässig im lokalen Log.
    from gui.main_window import main

    main()
