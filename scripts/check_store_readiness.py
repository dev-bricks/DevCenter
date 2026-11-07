"""
Store Readiness Preflight Check for DevCenter Suite.

Validates that all necessary metadata, documentation files, licenses,
icon assets, manifest resources, and staged 6-language Store listings
required for Windows Store release are present, valid, and policy-compliant
(Policy P-006 / Tier-2 / Microsoft Partner Center Policy 10.1.3).
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TIER2_LANGUAGES = ("de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU")


def check_store_package_json(project_root: Path) -> List[str]:
    errors = []
    file_path = project_root / "store_package.json"
    if not file_path.exists():
        errors.append("store_package.json is missing.")
        return errors

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"store_package.json is invalid JSON: {e}")
        return errors

    required_fields = [
        "app_name",
        "publisher",
        "publisher_display",
        "identity_name",
        "version",
        "description",
        "executable",
        "capabilities",
        "category",
        "age_rating",
        "privacy_url",
        "support_url",
        "license",
        "languages",
    ]
    for field in required_fields:
        val = data.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            errors.append(f"store_package.json field '{field}' is missing or empty.")
        elif field == "publisher" and (val.startswith("CN=YOUR-PUBLISHER-ID") or "YOUR-PUBLISHER" in val):
            errors.append("store_package.json publisher is still placeholder.")

    langs = data.get("languages", [])
    for lang in TIER2_LANGUAGES:
        if lang not in langs:
            errors.append(f"store_package.json missing Tier-2 language: '{lang}'")

    for lang_code in ("de", "en", "es", "zh", "ja", "ru"):
        desc_key = f"description_{lang_code}"
        desc_val = data.get(desc_key)
        if not desc_val:
            errors.append(f"store_package.json missing short description '{desc_key}'")
        elif len(desc_val) > 100:
            errors.append(f"store_package.json '{desc_key}' exceeds 100 chars ({len(desc_val)})")

        kw_key = f"keywords_{lang_code}"
        kw_val = data.get(kw_key)
        if not kw_val or not isinstance(kw_val, list):
            errors.append(f"store_package.json missing keyword list '{kw_key}'")
        elif len(kw_val) > 7:
            errors.append(f"store_package.json '{kw_key}' has {len(kw_val)} keywords (max 7 allowed)")
        else:
            for kw in kw_val:
                if len(kw) > 30:
                    errors.append(f"store_package.json keyword '{kw}' in '{kw_key}' exceeds 30 chars")

    return errors


def check_documentation_files(project_root: Path) -> List[str]:
    errors = []
    docs = [
        ("PRIVACY_POLICY.md", 200),
        ("SUPPORT.md", 100),
        ("STORE_LISTING.md", 200),
        ("WINDOWS_STORE_PREP.md", 100),
        ("THIRD_PARTY_LICENSES.txt", 100),
    ]

    for filename, min_len in docs:
        p = project_root / filename
        if not p.exists():
            errors.append(f"Required document '{filename}' is missing.")
        elif p.stat().st_size < min_len:
            errors.append(f"Document '{filename}' is suspiciously small ({p.stat().st_size} bytes).")

    return errors


def check_store_icon_assets(project_root: Path) -> List[str]:
    errors = []
    asset_dir = project_root / "store_assets"
    if not asset_dir.exists():
        asset_dir = project_root / "store_package" / "DevCenter" / "icons"

    if not asset_dir.exists():
        errors.append("Store icon directory (store_assets/ or store_package/DevCenter/icons/) is missing.")
        return errors

    expected_icons = [
        "Square44x44Logo.png",
        "Square150x150Logo.png",
        "Wide310x150Logo.png",
        "Square310x310Logo.png",
        "StoreLogo.png",
    ]

    for icon_name in expected_icons:
        icon_path = asset_dir / icon_name
        if not icon_path.exists():
            errors.append(f"Store icon '{icon_name}' is missing in {asset_dir.name}.")
        elif icon_path.stat().st_size < 100:
            errors.append(f"Store icon '{icon_name}' is suspiciously small ({icon_path.stat().st_size} bytes).")

    return errors


def check_store_listing_keywords(project_root: Path) -> List[str]:
    errors = []
    listing_path = project_root / "STORE_LISTING.md"
    if not listing_path.exists():
        errors.append("STORE_LISTING.md is missing.")
        return errors

    content = listing_path.read_text(encoding="utf-8")
    for section_name in ("Deutsch", "English", "Español", "简体中文", "日本語", "Русский"):
        if f"## {section_name}" not in content:
            errors.append(f"STORE_LISTING.md missing section for '## {section_name}'")

    for kw_header in (
        "### Schlüsselwörter",
        "### Keywords",
        "### Palabras clave",
        "### 关键词",
        "### 关键字",
        "### キーワード",
        "### Ключевые слова",
    ):
        m = re.search(re.escape(kw_header) + r"[^\n]*\s*\n([^\n#]+)", content)
        if m:
            keywords = [k.strip() for k in m.group(1).split(",") if k.strip()]
            if len(keywords) > 7:
                errors.append(f"STORE_LISTING.md has {len(keywords)} keywords under '{kw_header}' (max 7 allowed).")

    return errors


def check_staging_files(project_root: Path) -> List[str]:
    errors = []
    stage_dir = project_root / "releases" / "windowsstore"
    if not stage_dir.exists():
        errors.append("releases/windowsstore/ directory is missing.")
        return errors

    staged_files = [
        "BUILD.md",
        "WACK_PROTOCOL.md",
        "store_settings.json",
        "store_listing_de.md",
        "store_listing_en.md",
        "store_listing_es.md",
        "store_listing_zh.md",
        "store_listing_ja.md",
        "store_listing_ru.md",
    ]
    for sf in staged_files:
        p = stage_dir / sf
        if not p.exists():
            errors.append(f"Staged file '{sf}' is missing in releases/windowsstore/")
        elif p.stat().st_size < 50:
            errors.append(f"Staged file '{sf}' is unexpectedly small ({p.stat().st_size} bytes)")

    return errors


def check_manifest_xml(project_root: Path) -> List[str]:
    errors = []
    manifest_path = project_root / "store_package" / "DevCenter" / "AppxManifest.xml"
    if not manifest_path.exists():
        errors.append("store_package/DevCenter/AppxManifest.xml is missing.")
        return errors

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
    except Exception as e:
        errors.append(f"AppxManifest.xml is not well-formed XML: {e}")
        return errors

    # Check namespaces
    ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}

    identity = root.find("m:Identity", ns)
    if identity is None:
        identity = root.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity")

    if identity is None:
        errors.append("AppxManifest.xml missing Identity element.")
    else:
        name = identity.attrib.get("Name")
        if name != "Geiger.DevCenterSuite":
            errors.append(f"AppxManifest.xml Identity Name is '{name}', expected 'Geiger.DevCenterSuite'.")

    # Check resources
    resources = root.find("m:Resources", ns)
    if resources is None:
        resources = root.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Resources")

    if resources is None:
        errors.append("AppxManifest.xml missing Resources element.")
    else:
        manifest_langs = []
        for child in resources:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "Resource":
                lang = child.attrib.get("Language")
                if lang:
                    manifest_langs.append(lang.lower())
        for expected in ("de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"):
            if expected not in manifest_langs:
                errors.append(f"AppxManifest.xml Resources missing language: '{expected}'.")

    return errors


def check_url_reachability(project_root: Path) -> List[str]:
    """Validates that privacy_url and support_url are syntactically valid HTTPS URLs."""
    errors = []
    file_path = project_root / "store_package.json"
    if not file_path.exists():
        return errors

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return errors

    for field in ("privacy_url", "support_url"):
        url = data.get(field)
        if not url or not isinstance(url, str) or not url.strip():
            continue
        if not url.startswith("https://"):
            errors.append(f"store_package.json field '{field}' must use HTTPS: {url}")

    return errors


def run_store_readiness_check(project_root: Path = PROJECT_ROOT) -> Tuple[bool, List[str]]:
    all_errors = []
    all_errors.extend(check_store_package_json(project_root))
    all_errors.extend(check_documentation_files(project_root))
    all_errors.extend(check_store_icon_assets(project_root))
    all_errors.extend(check_store_listing_keywords(project_root))
    all_errors.extend(check_staging_files(project_root))
    all_errors.extend(check_manifest_xml(project_root))
    all_errors.extend(check_url_reachability(project_root))

    success = len(all_errors) == 0
    return success, all_errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Store Readiness Preflight Check")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT), help="Project root path")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    target_root = Path(args.project_root).resolve()
    success, errors = run_store_readiness_check(target_root)

    if args.json:
        result = {
            "success": success,
            "findings_count": len(errors),
            "findings": errors,
            "project_root": str(target_root),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Store Readiness Audit for: {target_root.name}")
        print(f"Path: {target_root}")
        print("-" * 60)
        if success:
            print("STORE READINESS CHECK PASSED: 0 findings. Project is Store-ready.")
        else:
            print(f"STORE READINESS CHECK FAILED: {len(errors)} findings detected:")
            for idx, err in enumerate(errors, 1):
                print(f"  [{idx:02d}] {err}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
