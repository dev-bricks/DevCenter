"""Guard the release license inventory against dependency drift."""

import json
import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _dependency_names():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    return [
        re.split(r"[<>=!~;\[]", requirement, 1)[0].strip()
        for requirement in dependencies
    ]


def test_third_party_license_inventory_covers_project_dependencies():
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")

    assert "Checked: 2026-07-02" in inventory
    assert "licensed under GPL-3.0-only according to `LICENSE`" in inventory
    assert "not a frozen transitive SBOM" in inventory

    inventory_lower = inventory.lower()
    for package in _dependency_names():
        assert f"| {package.lower()} " in inventory_lower

    for package in ("PySide6_Addons", "PySide6_Essentials", "shiboken6"):
        assert f"| {package}" in inventory


def test_web_companion_has_no_undocumented_runtime_dependencies():
    companion_pkg = ROOT / "web_companion" / "package.json"
    if not companion_pkg.exists():
        return
    package_json = json.loads(companion_pkg.read_text(encoding="utf-8"))
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")

    assert not package_json.get("dependencies")
    assert not package_json.get("devDependencies")
    assert "`web_companion/package.json` has no dependencies or devDependencies" in inventory

