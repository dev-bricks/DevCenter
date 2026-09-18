# -*- coding: utf-8 -*-
"""
DevCenter - Python Development Suite
Haupteinstiegspunkt der Anwendung

Starten mit:
    python main.py
oder mit CLI-Optionen:
    python main.py --help
    python main.py --version
    python main.py --check
    python main.py --open <pfad>
    python main.py --analyze <pfad>
    python main.py --export-workspace <pfad>
    python main.py --debug
"""

import sys
import os

# Pfade zu Root und src-Verzeichnis hinzufügen
root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(root_dir, "src")
for p in (src_dir, root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.gui.main_window import main

if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code or 0)
