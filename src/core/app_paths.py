# -*- coding: utf-8 -*-
"""Plattformgerechte Standardpfade für DevCenter."""

from __future__ import annotations

import os
import sys
from pathlib import Path


APP_DIR_NAME = "DevCenter"


def get_app_data_dir() -> Path:
    """Liefert den plattformgerechten Konfigurationsordner für DevCenter."""
    if sys.platform.startswith("win"):
        app_data = os.environ.get("APPDATA")
        base_dir = Path(app_data) if app_data else Path(os.path.expanduser("~"))
        return base_dir / APP_DIR_NAME

    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        xdg_path = Path(xdg_config).expanduser()
        if xdg_path.is_absolute():
            return xdg_path / APP_DIR_NAME

    return Path(os.path.expanduser("~")) / ".config" / APP_DIR_NAME


def get_settings_path() -> Path:
    """Liefert den Standardpfad zur Einstellungsdatei."""
    return get_app_data_dir() / "settings.json"


def get_file_index_path() -> Path:
    """Liefert den Standardpfad zur lokalen Dateiindex-Datenbank."""
    return get_app_data_dir() / "file_index.db"
