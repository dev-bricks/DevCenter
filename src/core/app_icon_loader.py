"""App-Icon-Loader für DevCenter.

Lädt das Anwendungs-Icon mit robuster Multi-Pfad-Auflösung (PyInstaller-Bundle,
assets/app_icon.ico, assets/DevCenter.ico, Root-ICOs und PNG-Fallback)
sowohl als PIL-Image (für System-Tray / Bildbearbeitung) als auch optional als QIcon.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL import Image


def get_project_root() -> Path:
    """Liefert das Basisverzeichnis für Ressourcen im Repo oder gefrorenen Bundle."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def get_app_icon_path() -> Path | None:
    """Findet den besten verfügbaren Pfad zur Icon-Datei."""
    root = get_project_root()
    candidates = [
        root / "assets" / "DevCenter.ico",
        root / "assets" / "app_icon.ico",
        root / "assets" / "DesktopIcon.ico",
        root / "assets" / "icon.ico",
        root / "DevCenter.ico",
        root / "DesktopIcon.ico",
        root / "icon.ico",
        root / "ICO.ico",
        root / "assets" / "DesktopIcon.png",
        root / "assets" / "icon.png",
        root / "assets" / "DevCenter.png",
        root / "DesktopIcon.png",
        root / "icon.png",
        root / "DevCenter.png",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def load_app_icon_pil(size: int = 64) -> Image.Image:
    """Lädt das Anwendungs-Icon als PIL Image mit Fallback."""
    from PIL import Image, ImageDraw

    icon_path = get_app_icon_path()
    if icon_path is not None:
        try:
            with Image.open(icon_path) as img:
                return img.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Deterministischer Fallback falls Datei nicht lesbar
    image = Image.new("RGBA", (size, size), (8, 15, 30, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 3, size - 4, size - 4), radius=max(2, size // 5), fill=(8, 15, 30, 255))
    draw.polygon(
        [
            (size * 0.5, size * 0.15),
            (size * 0.8, size * 0.3),
            (size * 0.8, size * 0.7),
            (size * 0.5, size * 0.85),
            (size * 0.2, size * 0.7),
            (size * 0.2, size * 0.3),
        ],
        fill=(0, 82, 255, 255),
    )
    draw.arc(
        (size * 0.25, size * 0.25, size * 0.75, size * 0.75),
        0,
        360,
        fill=(0, 229, 255, 255),
        width=max(1, size // 16),
    )
    return image


def load_app_icon() -> Any:
    """Lädt ein valides QIcon falls PySide6/PyQt verfügbar ist, sonst None."""
    try:
        from PySide6.QtGui import QGuiApplication, QIcon
    except ImportError:
        try:
            from PyQt6.QtGui import QGuiApplication, QIcon
        except ImportError:
            return None

    if QGuiApplication.instance() is None:
        try:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            _ = QGuiApplication([])
        except Exception:
            return None

    icon_path = get_app_icon_path()
    if icon_path is not None:
        try:
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                return icon
        except Exception:
            pass

    return QIcon()


def get_app_icon() -> Any:
    """Alias für load_app_icon."""
    return load_app_icon()
