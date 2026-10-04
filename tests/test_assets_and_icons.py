"""Vertragstests für App-Icons und Asset-Suiten von DevCenter.

Prüft Master-Icons, Multi-Layer Windows-ICOs, Assets-Parität,
Mobile/PWA-Suite, Store-Assets und Laufzeit-Icon-Lader.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _read_ico_sizes(ico_path: Path) -> list[tuple[int, int]]:
    with open(ico_path, "rb") as f:
        _reserved, ico_type, count = struct.unpack("<HHH", f.read(6))
        assert ico_type == 1, f"{ico_path.name} ist keine gültige ICO-Datei"
        sizes: list[tuple[int, int]] = []
        for _ in range(count):
            w, h, _colors, _res, _planes, _bpp, _size, _offset = struct.unpack(
                "<BBBBHHII", f.read(16)
            )
            sizes.append((w or 256, h or 256))
        return sizes


def test_master_icons_exist() -> None:
    desktop_png = PROJECT_ROOT / "DesktopIcon.png"
    icon_png = PROJECT_ROOT / "icon.png"
    app_png = PROJECT_ROOT / "DevCenter.png"
    desktop_ico = PROJECT_ROOT / "DesktopIcon.ico"
    app_ico = PROJECT_ROOT / "DevCenter.ico"
    root_ico = PROJECT_ROOT / "ICO.ico"
    icon_ico = PROJECT_ROOT / "icon.ico"
    fav_ico = PROJECT_ROOT / "favicon.ico"
    fav_png = PROJECT_ROOT / "favicon.png"

    for path in (desktop_png, icon_png, app_png, desktop_ico, app_ico, root_ico, icon_ico, fav_ico, fav_png):
        assert path.is_file(), f"{path.name} fehlt im Root"

    for png_file in (desktop_png, icon_png, app_png):
        with Image.open(png_file) as img:
            assert img.size == (1024, 1024), f"{png_file.name} muss 1024x1024 sein"

    for ico_file in (desktop_ico, app_ico, root_ico, icon_ico):
        sizes = _read_ico_sizes(ico_file)
        assert len(sizes) == 7, f"{ico_file.name} muss 7 Layer haben, hat {len(sizes)}"
        assert (16, 16) in sizes
        assert (24, 24) in sizes
        assert (32, 32) in sizes
        assert (48, 48) in sizes
        assert (64, 64) in sizes
        assert (128, 128) in sizes
        assert (256, 256) in sizes

    sizes_fav = _read_ico_sizes(fav_ico)
    assert len(sizes_fav) >= 4, "favicon.ico muss mindestens 4 Layer haben"
    assert (16, 16) in sizes_fav and (32, 32) in sizes_fav


def test_assets_folder_parity() -> None:
    assets_dir = PROJECT_ROOT / "assets"
    assert assets_dir.is_dir(), "assets/ Verzeichnis fehlt"

    icon_png = assets_dir / "icon.png"
    desktop_png = assets_dir / "DesktopIcon.png"
    app_png = assets_dir / "DevCenter.png"
    icon_ico = assets_dir / "icon.ico"
    app_icon_ico = assets_dir / "app_icon.ico"
    app_ico = assets_dir / "DevCenter.ico"
    desktop_ico = assets_dir / "DesktopIcon.ico"
    favicon_png = assets_dir / "favicon.png"
    favicon_ico = assets_dir / "favicon.ico"

    for path in (icon_png, desktop_png, app_png, icon_ico, app_icon_ico, app_ico, desktop_ico, favicon_png, favicon_ico):
        assert path.is_file(), f"assets/{path.name} fehlt"

    for png_file in (icon_png, desktop_png, app_png):
        with Image.open(png_file) as img:
            assert img.size == (1024, 1024), f"assets/{png_file.name} muss 1024x1024 sein"

    with Image.open(favicon_png) as img:
        assert img.size in ((32, 32), (64, 64)), "assets/favicon.png muss 32x32 oder 64x64 sein"

    for ico_file in (app_icon_ico, app_ico, icon_ico, desktop_ico):
        sizes = _read_ico_sizes(ico_file)
        assert len(sizes) == 7, f"{ico_file.name} muss 7 Layer haben"
        assert (24, 24) in sizes, f"{ico_file.name} fehlt 24x24 Layer"

    fav_sizes = _read_ico_sizes(favicon_ico)
    assert (16, 16) in fav_sizes and (32, 32) in fav_sizes


def test_mobile_pwa_icons_and_manifest() -> None:
    mobile_dir = PROJECT_ROOT / "mobile_icons"
    assert mobile_dir.is_dir(), "mobile_icons/ Verzeichnis fehlt"

    required_files = [
        "icon.png",
        "icon-192.png",
        "icon-512.png",
        "icon-maskable-192.png",
        "icon-maskable-512.png",
        "apple-touch-icon.png",
        "apple-touch-icon-180.png",
        "favicon.png",
        "favicon.ico",
        "manifest.json",
    ]
    for fname in required_files:
        path = mobile_dir / fname
        assert path.is_file(), f"mobile_icons/{fname} fehlt"

    with Image.open(mobile_dir / "icon.png") as img:
        assert img.size == (1024, 1024)
    with Image.open(mobile_dir / "icon-192.png") as img:
        assert img.size == (192, 192)
    with Image.open(mobile_dir / "icon-512.png") as img:
        assert img.size == (512, 512)
    with Image.open(mobile_dir / "icon-maskable-192.png") as img:
        assert img.size == (192, 192)
    with Image.open(mobile_dir / "icon-maskable-512.png") as img:
        assert img.size == (512, 512)
    with Image.open(mobile_dir / "apple-touch-icon.png") as img:
        assert img.size == (180, 180)
    with Image.open(mobile_dir / "apple-touch-icon-180.png") as img:
        assert img.size == (180, 180)

    icons_sub = mobile_dir / "icons"
    assert icons_sub.is_dir(), "mobile_icons/icons/ fehlt"
    for fname in ("Icon-192.png", "Icon-512.png", "Icon-maskable-192.png", "Icon-maskable-512.png"):
        assert (icons_sub / fname).is_file(), f"mobile_icons/icons/{fname} fehlt"

    manifest_data = json.loads((mobile_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_data["name"] == "DevCenter"
    assert manifest_data["short_name"] == "DevCenter"
    assert len(manifest_data["icons"]) >= 4
    for icon_entry in manifest_data["icons"]:
        icon_path = mobile_dir / icon_entry["src"]
        assert icon_path.is_file(), f"Manifest-Icon nicht gefunden: {icon_entry['src']}"


def test_store_assets() -> None:
    store_dir = PROJECT_ROOT / "store_assets"
    assert store_dir.is_dir(), "store_assets/ Verzeichnis fehlt"

    expected_sizes = {
        "icon_44x44.png": (44, 44),
        "Square44x44Logo.png": (44, 44),
        "icon_50x50.png": (50, 50),
        "Square50x50Logo.png": (50, 50),
        "StoreLogo.png": (50, 50),
        "icon_150x150.png": (150, 150),
        "Square150x150Logo.png": (150, 150),
        "icon_310x150.png": (310, 150),
        "Wide310x150Logo.png": (310, 150),
        "icon_310x310.png": (310, 310),
        "Square310x310Logo.png": (310, 310),
    }
    for filename, expected_size in expected_sizes.items():
        file_path = store_dir / filename
        assert file_path.is_file(), f"store_assets/{filename} fehlt"
        with Image.open(file_path) as img:
            assert img.size == expected_size, (
                f"{filename} hat Größe {img.size}, erwartet {expected_size}"
            )

    readme_path = store_dir / "README.md"
    assert readme_path.is_file(), "store_assets/README.md fehlt"


def test_app_icon_loader_returns_valid_icon() -> None:
    from core.app_icon_loader import (
        get_app_icon,
        get_app_icon_path,
        get_project_root,
        load_app_icon,
        load_app_icon_pil,
    )

    root = get_project_root()
    assert root == PROJECT_ROOT

    path = get_app_icon_path()
    assert path is not None
    assert path.is_file()

    img = load_app_icon_pil(size=64)
    assert img.size == (64, 64)
    assert img.mode == "RGBA"
    # Ensure there are visible non-transparent pixels
    assert img.getextrema()[3][1] > 0

    # Qt loader should be callable without exception
    _ = load_app_icon()
    _ = get_app_icon()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main(["-v", __file__]))
