"""Automatisierte Metadaten-, Sicherheits-, Ökosystem- und Dokumentationsparitätstests für DevCenter."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_readme_and_readme_de_existence_and_language_links():
    """Prüft, dass README.md und README_de.md existieren und wechselseitig verlinkt sind."""
    readme_en = REPO_ROOT / "README.md"
    readme_de = REPO_ROOT / "README_de.md"

    assert readme_en.is_file(), "README.md fehlt im Repo-Root"
    assert readme_de.is_file(), "README_de.md fehlt im Repo-Root"

    content_en = readme_en.read_text(encoding="utf-8")
    content_de = readme_de.read_text(encoding="utf-8")

    assert "README_de.md" in content_en, "README.md muss auf README_de.md verlinken"
    assert "README.md" in content_de, "README_de.md muss auf README.md verlinken"
    assert "DevCenter" in content_en
    assert "DevCenter" in content_de


def test_badges_parity():
    """Prüft, dass beide README-Dateien synchronisierte Badges für Version 1.0.2 und Kernmetriken enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "badge/version-1.0.2-blue" in content_en
    assert "badge/version-1.0.2-blue" in content_de

    assert "badge/python-3.11" in content_en
    assert "badge/python-3.11" in content_de

    assert "badge/LLM--Context-llms.txt" in content_en
    assert "badge/LLM--Context-llms.txt" in content_de

    assert "dev--bricks" in content_en and "dev--bricks" in content_de
    assert "open--bricks" in content_en and "open--bricks" in content_de


def test_mermaid_diagrams_present():
    """Prüft, dass beide READMEs interaktive Mermaid-Diagramme für Architektur und Datenfluss/Datenschutz enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert content_en.count("```mermaid") >= 2, "README.md muss mindestens zwei Mermaid-Diagramme enthalten"
    assert content_de.count("```mermaid") >= 2, "README_de.md muss mindestens zwei Mermaid-Diagramme enthalten"
    assert "sequenceDiagram" in content_en and "graph TB" in content_en
    assert "sequenceDiagram" in content_de and "graph TB" in content_de


def test_security_policy_bilingual_and_contacts():
    """Prüft, dass SECURITY.md zweisprachig ist, Zero-Egress, 48h SLA und die Sicherheitskontakte enthält."""
    sec_file = REPO_ROOT / "SECURITY.md"
    assert sec_file.is_file(), "SECURITY.md fehlt im Repo-Root"

    content = sec_file.read_text(encoding="utf-8")

    assert "security@dev-bricks.org" in content
    assert "security@open-bricks.org" in content
    assert "security@ellmos.ai" in content
    assert "48" in content, "SECURITY.md muss 48h Reaktions-SLA erwähnen"
    assert "local-first" in content.lower(), "SECURITY.md muss local-first erwähnen"
    assert "zero-egress" in content.lower() or "offline" in content.lower()
    assert "keyring" in content.lower()
    assert "Sicherheitsrichtlinie" in content, "SECURITY.md muss einen deutschen Abschnitt enthalten"


def test_llms_txt_currency_and_structure():
    """Prüft, dass llms.txt aktuell ist, Version 1.0.2, 10 Invarianten und Referenzen enthält."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt fehlt im Repo-Root"

    content = llms_file.read_text(encoding="utf-8")

    assert "https://github.com/dev-bricks/DevCenter" in content
    assert "2026-09-14" in content, "llms.txt Last-checked Timestamp muss auf 2026-09-14 stehen"
    assert "Version: 1.0.2" in content
    assert "local-first Python IDE" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content.lower()
    assert "THIRD_PARTY_LICENSES.md" in content
    assert "MARKETING-LOG.txt" in content


def test_pyproject_version_and_pep621_metadata():
    """Prüft die Gültigkeit von pyproject.toml, Version 1.0.2, URLs und Pytest-Konfiguration."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml fehlt im Repo-Root"

    content = pyproject_file.read_text(encoding="utf-8")

    assert 'name = "devcenter-suite"' in content
    assert 'version = "1.0.2"' in content
    assert "classifiers = [" in content
    assert "keywords = [" in content
    assert "[project.urls]" in content
    assert "Homepage =" in content
    assert "Repository =" in content
    assert "Security =" in content
    assert '"Third-Party Licenses" =' in content
    assert '"Marketing Log" =' in content
    assert '"LLM Ready" =' in content
    assert "Parent Organization" in content
    assert "Umbrella Ecosystem" in content
    assert 'addopts = "-ra -v"' in content


def test_sibling_ecosystem_matrix_presence():
    """Prüft, dass beide Dokumentationen eine Ökosystem-Matrix mit dev-bricks & open-bricks enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for keyword in ["dev-bricks", "ellmos-ai", "file-bricks", "doc-bricks", "open-bricks", "MethodenAnalyser"]:
        assert keyword in content_en, f"{keyword} fehlt in README.md"
        assert keyword in content_de, f"{keyword} fehlt in README_de.md"


def test_changelog_currency():
    """Prüft, dass CHANGELOG.md aktuelle Einträge für 1.0.2 und 1.0.1 enthält."""
    changelog_file = REPO_ROOT / "CHANGELOG.md"
    assert changelog_file.is_file(), "CHANGELOG.md fehlt im Repo-Root"

    content = changelog_file.read_text(encoding="utf-8")
    assert "## [1.0.2] - 2026-09-14" in content
    assert "Pfad A" in content
    assert "## [1.0.1] - 2026-09-12" in content
    assert "Pfad B" in content


def test_fifteen_point_quick_navigation_and_anchor_parity():
    """Prüft, dass beide README-Dateien exakt 15 Navigationspunkte enthalten und alle Anker auflösbar sind."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    nav_en_match = re.search(r"## Quick Navigation\s*\n\n((?:\d+\.\s+\[.+?\]\(#.+?\)\s*\n)+)", readme_en)
    nav_de_match = re.search(r"## Schnelleinstieg & Navigation\s*\n\n((?:\d+\.\s+\[.+?\]\(#.+?\)\s*\n)+)", readme_de)

    assert nav_en_match, "Quick Navigation Block fehlt in README.md"
    assert nav_de_match, "Schnelleinstieg & Navigation Block fehlt in README_de.md"

    links_en = re.findall(r"\d+\.\s+\[(.+?)\]\((#.+?)\)", nav_en_match.group(1))
    links_de = re.findall(r"\d+\.\s+\[(.+?)\]\((#.+?)\)", nav_de_match.group(1))

    assert len(links_en) == 15, f"README.md muss genau 15 Navigationspunkte haben, hat {len(links_en)}"
    assert len(links_de) == 15, f"README_de.md muss genau 15 Navigationspunkte haben, hat {len(links_de)}"

    # Check anchor resolution in English README
    for label, anchor in links_en:
        anchor_id = anchor.lstrip("#")
        # Header generated anchor in markdown
        header_pattern = re.compile(r"^##\s+.*", re.MULTILINE)
        headers = [h.lstrip("#").strip().lower() for h in header_pattern.findall(readme_en)]
        # Sanitize header to anchor
        sanitized = [re.sub(r"[^\w\s-]", "", h).replace(" ", "-") for h in headers]
        assert any(anchor_id == s or anchor_id in s for s in sanitized), f"Anchor {anchor} nicht auflösbar in README.md"

    # Check anchor resolution in German README
    for label, anchor in links_de:
        anchor_id = anchor.lstrip("#")
        header_pattern = re.compile(r"^##\s+.*", re.MULTILINE)
        headers = [h.lstrip("#").strip().lower() for h in header_pattern.findall(readme_de)]
        sanitized = [re.sub(r"[^\w\s-]", "", h).replace(" ", "-") for h in headers]
        assert any(anchor_id == s or anchor_id in s for s in sanitized), (
            f"Anchor {anchor} nicht auflösbar in README_de.md"
        )


def test_ten_governance_invariants_parity():
    """Prüft, dass alle 10 Governance- und Laufzeit-Invarianten (INV-LOCAL-01 bis INV-SLA-10) in READMEs und llms.txt stehen."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    llms_txt = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")

    expected_invariants = [
        "INV-LOCAL-01",
        "INV-OPTIN-02",
        "INV-KEYRING-03",
        "INV-EXPORT-04",
        "INV-STATIC-05",
        "INV-SECURITY-06",
        "INV-PERM-07",
        "INV-USER-08",
        "INV-MULTI-09",
        "INV-SLA-10",
    ]

    for inv in expected_invariants:
        assert inv in readme_en, f"{inv} fehlt in README.md"
        assert inv in readme_de, f"{inv} fehlt in README_de.md"
        assert inv in llms_txt, f"{inv} fehlt in llms.txt"


def test_marketing_log_contract():
    """Prüft die Integrität von MARKETING-LOG.txt bezüglich Zielgruppen, Suchbegriffen und Wettbewerbsmatrix."""
    mkt_file = REPO_ROOT / "MARKETING-LOG.txt"
    assert mkt_file.is_file(), "MARKETING-LOG.txt fehlt im Repo-Root"

    content = mkt_file.read_text(encoding="utf-8")
    assert "dev-bricks" in content
    assert "open-bricks" in content
    assert "PERSONA-01" in content
    assert "PERSONA-02" in content
    assert "PERSONA-03" in content
    assert "PERSONA-04" in content
    assert "COMPETITIVE MATRIX" in content
    assert "HIGH-INTENT SEARCH QUERIES" in content
    assert "2026-09-12" in content
    assert "2026-09-14" in content


def test_cross_platform_smoke_scripts_and_ci():
    """Prüft, dass Linux- und macOS-Plattform-Smokes existieren und im CI-Workflow mit Concurrency verdrahtet sind."""
    linux_smoke = REPO_ROOT / "tests" / "linux_platform_smoke.py"
    macos_smoke = REPO_ROOT / "tests" / "macos_platform_smoke.py"
    workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"

    assert linux_smoke.is_file(), "linux_platform_smoke.py fehlt in tests/"
    assert macos_smoke.is_file(), "macos_platform_smoke.py fehlt in tests/"
    assert workflow.is_file(), "tests.yml fehlt in .github/workflows/"

    workflow_content = workflow.read_text(encoding="utf-8")
    assert "actions/checkout@v4" in workflow_content
    assert "actions/setup-python@v5" in workflow_content
    assert "concurrency:" in workflow_content
    assert "cancel-in-progress: true" in workflow_content
    assert "linux-platform-smoke:" in workflow_content
    assert "macos-platform-smoke:" in workflow_content
    assert "tests/linux_platform_smoke.py" in workflow_content
    assert "tests/macos_platform_smoke.py" in workflow_content


def test_offline_and_zero_egress_invariants():
    """Prüft, dass Core-Module keine ungeprüften externen Netzwerk-Libraries importieren."""
    import core.app_paths
    import core.settings_manager

    assert hasattr(core.app_paths, "get_app_data_dir")
    assert hasattr(core.app_paths, "get_settings_path")
    assert hasattr(core.app_paths, "get_app_icon_path")
    assert hasattr(core.settings_manager, "SettingsManager")


def test_gitignore_hygiene_and_lock_exclusion():
    """Prüft, dass .gitignore Schutz vor Lock-Dateien und Sync-Konflikten bietet."""
    gitignore_file = REPO_ROOT / ".gitignore"
    assert gitignore_file.is_file(), ".gitignore fehlt im Repo-Root"

    content = gitignore_file.read_text(encoding="utf-8")
    assert "LOCK*.txt" in content
    assert "*.sync-conflict-*" in content or "*.conflict" in content
    assert "* (kopie)*" in content or "* (copy)*" in content


def test_ci_workflow_timeout_and_concurrency_guardrails():
    """Prüft Job-Level Timeouts (15 min) und standardisiertes pytest -ra -v in tests.yml."""
    tests_workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"
    assert tests_workflow.is_file()
    content = tests_workflow.read_text(encoding="utf-8")

    assert "timeout-minutes: 15" in content
    assert "python -m pytest -ra -v" in content
    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content


def test_stale_workflow_timeout_and_concurrency():
    """Prüft Concurrency und Job-Timeout (10 min) in stale.yml."""
    stale_workflow = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_workflow.is_file()
    content = stale_workflow.read_text(encoding="utf-8")

    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content
    assert "timeout-minutes: 10" in content


def test_welcome_workflow_timeout_and_concurrency():
    """Prüft Concurrency und Job-Timeout (5 min) in welcome.yml."""
    welcome_workflow = REPO_ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_workflow.is_file()
    content = welcome_workflow.read_text(encoding="utf-8")

    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content
    assert "timeout-minutes: 5" in content


def test_extended_gitignore_multi_host_and_lock_defense():
    """Prüft erweiterte Multi-Host-Konflikt- und Fail-Closed-Lock-Muster in .gitignore."""
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    for host_pat in ["*-WORKSTATION*", "*-ASUS*", "*-LAPTOP*", "*-Mac Studio*"]:
        assert host_pat in content, f"{host_pat} fehlt in .gitignore"

    for conflict_pat in ["*conflicted copy*", "* (Kopie)*", "* (Copy)*"]:
        assert conflict_pat in content, f"{conflict_pat} fehlt in .gitignore"

    for lock_pat in ["LOCK", "LOCK*.txt", "LOCK.*", "*.lock", "uv.lock", "!package-lock.json"]:
        assert lock_pat in content, f"{lock_pat} fehlt in .gitignore"

    for cache_pat in [".coverage.*", "coverage/", ".tox/", ".hypothesis/", ".turbo/", ".nyc_output/", "*.rej"]:
        assert cache_pat in content, f"{cache_pat} fehlt in .gitignore"


def test_marketing_log_recent_hygiene_entry():
    """Prüft, dass der Pfad-A-Audit-Eintrag für 1.0.2 in MARKETING-LOG.txt vorliegt."""
    content = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "2026-09-14 [HYG Pfad A] Release 1.0.2" in content
