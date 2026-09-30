"""Automatisierte Metadaten-, Sicherheits-, Ökosystem- und Dokumentationsparitätstests für DevCenter."""

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

    assert "badge/version-1.0.3-blue" in content_en
    assert "badge/version-1.0.3-blue" in content_de

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
    """Prüft, dass llms.txt aktuell ist, Version 1.0.3, 10 Invarianten und Referenzen enthält."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt fehlt im Repo-Root"

    content = llms_file.read_text(encoding="utf-8")

    assert "https://github.com/dev-bricks/DevCenter" in content
    assert "2026-09-28" in content, "llms.txt Last-checked Timestamp muss auf 2026-09-28 stehen"
    assert "Version: 1.0.3" in content
    assert "local-first Python IDE" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content.lower()
    assert "THIRD_PARTY_LICENSES.md" in content
    assert "MARKETING-LOG.txt" in content
    assert "NOTICE" in content


def test_pyproject_version_and_pep621_metadata():
    """Prüft die Gültigkeit von pyproject.toml, Version 1.0.3, URLs und Pytest-Konfiguration."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml fehlt im Repo-Root"

    content = pyproject_file.read_text(encoding="utf-8")

    assert 'name = "devcenter-suite"' in content
    assert 'version = "1.0.3"' in content
    assert "license-files = [" in content
    assert "classifiers = [" in content
    assert "keywords = [" in content
    assert "[project.urls]" in content
    assert "Homepage =" in content
    assert "Repository =" in content
    assert "Security =" in content
    assert "Notice =" in content
    assert '"Third-Party Licenses" =' in content
    assert '"Marketing Log" =' in content
    assert '"LLM Ready" =' in content
    assert "Parent Organization" in content
    assert "Umbrella Ecosystem" in content
    assert 'addopts = "-ra -v --basetemp=.pytest_temp"' in content


def test_sibling_ecosystem_matrix_presence():
    """Prüft, dass beide Dokumentationen eine Ökosystem-Matrix mit dev-bricks & open-bricks enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for keyword in ["dev-bricks", "ellmos-ai", "file-bricks", "doc-bricks", "open-bricks", "MethodenAnalyser"]:
        assert keyword in content_en, f"{keyword} fehlt in README.md"
        assert keyword in content_de, f"{keyword} fehlt in README_de.md"


def test_changelog_currency():
    """Prüft, dass CHANGELOG.md aktuelle Einträge für 1.0.3, 1.0.2 und 1.0.1 enthält."""
    changelog_file = REPO_ROOT / "CHANGELOG.md"
    assert changelog_file.is_file(), "CHANGELOG.md fehlt im Repo-Root"

    content = changelog_file.read_text(encoding="utf-8")
    assert "## [1.0.3] - 2026-09-16" in content
    assert "## [1.0.2] - 2026-09-14" in content
    assert "Pfad A" in content
    assert "## [1.0.1] - 2026-09-12" in content
    assert "Pfad B" in content


def test_eighteen_point_quick_navigation_and_anchor_parity():
    """Prüft, dass beide README-Dateien exakt 18 Navigationspunkte und reziproke duale Anker sec-01 bis sec-18 enthalten."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## 🧭 Quick Navigation" in readme_en or "## Quick Navigation" in readme_en
    assert "## 🧭 Schnelleinstieg & Navigation" in readme_de or "## Schnelleinstieg & Navigation" in readme_de

    for i in range(1, 19):
        assert f"[{i}. " in readme_en, f"README.md fehlt Navigationspunkt {i}"
        assert f"[{i}. " in readme_de, f"README_de.md fehlt Navigationspunkt {i}"
        sec_id = f'id="sec-{i:02d}"'
        assert sec_id in readme_en, f"README.md fehlt dualer Anker {sec_id}"
        assert sec_id in readme_de, f"README_de.md fehlt dualer Anker {sec_id}"


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
    assert "2026-09-28" in content


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
    assert hasattr(core.app_paths, "get_logs_dir")
    assert hasattr(core.app_paths, "get_log_file_path")
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
    """Prüft, dass die Pfad-A-Audit-Einträge für 1.0.3 und 1.0.2 in MARKETING-LOG.txt vorliegen."""
    content = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "2026-09-16 [HYG Pfad A] Release 1.0.3" in content
    assert "2026-09-14 [HYG Pfad A] Release 1.0.2" in content


def test_ci_workflow_no_duplicate_headers():
    """Prüft, dass workflows/tests.yml keine duplizierten Top-Level-Blöcke oder Header aufweist."""
    workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"
    assert workflow.is_file()
    content = workflow.read_text(encoding="utf-8")

    assert content.count("name: DevCenter CI & Smoke Tests") == 1
    assert content.count("concurrency:") == 1
    assert "permissions:\n  contents: read" in content


def test_pytest_ini_options_guardrails():
    """Prüft standardisierte minversion, norecursedirs und addopts in pyproject.toml."""
    pyproject = REPO_ROOT / "pyproject.toml"
    assert pyproject.is_file()
    content = pyproject.read_text(encoding="utf-8")

    assert 'minversion = "7.0"' in content
    assert 'addopts = "-ra -v --basetemp=.pytest_temp"' in content
    assert "norecursedirs = [" in content
    assert ".pytest_temp" in content


def test_canonical_notice_file_present_and_licensed():
    """Prüft, dass die kanonische NOTICE-Attributionsdatei existiert und Autoren enthält."""
    notice_file = REPO_ROOT / "NOTICE"
    assert notice_file.is_file(), "NOTICE-Datei fehlt im Repo-Root"
    content = notice_file.read_text(encoding="utf-8")
    assert "Lukas Geiger" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content
    assert "GPLv3" in content


def test_target_personas_contract():
    """Prüft, dass PERSONA-01 bis PERSONA-04 in beiden READMEs verankert sind."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    for persona in ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]:
        assert persona in readme_en, f"{persona} fehlt in README.md"
        assert persona in readme_de, f"{persona} fehlt in README_de.md"


def test_level_1_sbom_and_third_party_licenses_matrix():
    """Prüft Level 1 SBOM Invarianten-Kreuztabelle und Re-Audit-Datum in THIRD_PARTY_LICENSES.md."""
    tpl_file = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl_file.is_file()
    content = tpl_file.read_text(encoding="utf-8")
    assert "2026-09-28" in content
    assert "Level 1 SBOM Invariant Cross-Reference Matrix" in content
    assert "NOTICE" in content
    for inv in ["INV-LOCAL-01", "INV-OPTIN-02", "INV-KEYRING-03", "INV-SECURITY-06", "INV-PERM-07", "INV-USER-08", "INV-SLA-10"]:
        assert inv in content, f"{inv} fehlt in THIRD_PARTY_LICENSES.md"


def test_bgb_521_statutory_disclaimer_and_sla_parity():
    """Prüft § 521 BGB Gefälligkeitsrecht-Haftungsausschluss und 48h SLA."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    llms_txt = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")

    assert "521" in readme_en and "BGB" in readme_en
    assert "521" in readme_de and "BGB" in readme_de
    assert "521" in llms_txt and "BGB" in llms_txt
    assert "48h" in readme_en or "48-hour" in readme_en
    assert "48h" in readme_de or "48 Stunden" in readme_de


def test_ci_workflows_auto_assign_and_label_sync():
    """Prüft Bereitstellung und Härtung von auto-assign.yml, label-sync.yml und labels.yml."""
    auto_assign = REPO_ROOT / ".github" / "workflows" / "auto-assign.yml"
    label_sync = REPO_ROOT / ".github" / "workflows" / "label-sync.yml"
    labels_file = REPO_ROOT / ".github" / "labels.yml"

    assert auto_assign.is_file(), "auto-assign.yml fehlt"
    assert label_sync.is_file(), "label-sync.yml fehlt"
    assert labels_file.is_file(), "labels.yml fehlt"

    aa_content = auto_assign.read_text(encoding="utf-8")
    assert "concurrency:" in aa_content
    assert "cancel-in-progress: true" in aa_content
    assert "timeout-minutes: 5" in aa_content
    assert "actions/github-script@v7" in aa_content

    ls_content = label_sync.read_text(encoding="utf-8")
    assert "concurrency:" in ls_content
    assert "cancel-in-progress: true" in ls_content
    assert "timeout-minutes: 5" in ls_content
    assert "EndBug/label-sync@v2" in ls_content

    lbl_content = labels_file.read_text(encoding="utf-8")
    for standard_label in ["bug", "enhancement", "good first issue", "help wanted", "documentation", "duplicate", "wontfix", "priority: high", "priority: low", "needs-triage", "stale"]:
        assert standard_label in lbl_content, f"Standard-Label '{standard_label}' fehlt in labels.yml"


def test_third_party_licenses_plain_text_companion():
    """Prüft Level 1 SBOM plain-text companion file und alle 10 Governance-Invarianten."""
    txt_path = REPO_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert txt_path.is_file(), "THIRD_PARTY_LICENSES.txt fehlt"
    text = txt_path.read_text(encoding="utf-8")

    assert "Third-Party Licenses & Level 1 SBOM - DevCenter" in text
    assert "Canonical Notice: NOTICE" in text
    assert "THIRD_PARTY_LICENSES.md" in text
    assert "2026-09-30" in text
    assert "RunAsInvoker" in text

    invariants = [
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
    for inv in invariants:
        assert f"{inv}: PASS" in text, f"{inv} fehlt oder ist nicht mit PASS zertifiziert in THIRD_PARTY_LICENSES.txt"


def test_contributing_quality_gates_and_version_freeze():
    """Prüft Quality Gates, Invarianten und Version-Freeze Disziplin in CONTRIBUTING.md."""
    contrib_path = REPO_ROOT / "CONTRIBUTING.md"
    assert contrib_path.is_file(), "CONTRIBUTING.md fehlt"
    text = contrib_path.read_text(encoding="utf-8")

    assert "INV-LOCAL-01" in text
    assert "INV-SLA-10" in text
    assert "RunAsInvoker" in text
    assert "T-20260920-167562623" in text
    assert "1.0.3" in text
    assert "pytest" in text
    assert "ruff check" in text
    assert "compileall" in text


def test_pep621_plain_text_licenses_and_urls():
    """Prüft PEP 621 Standardisierung für Plain-Text Licenses und zusätzliche URLs."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.is_file()
    content = pyproject_file.read_text(encoding="utf-8")

    assert "THIRD_PARTY_LICENSES.txt" in content
    assert '"Third-Party Licenses (Text)" =' in content
    assert '"Plain-Text Licenses" =' in content
    assert '"Level 1 SBOM" =' in content
    assert "Contributing =" in content
    assert ".pytest_tmp*" in content


def test_extended_gitignore_ideapad_and_canonical_locks():
    """Prüft erweiterte Multi-Host-Tokens und kanonische Locks in .gitignore."""
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    for pat in ["*-IDEAPAD*", "*-IDEAPAD-GEI*", "*-WORKSTATION.*", "*-WORKSTATION-LG.*", "*-MacBook*", "Desktop.ini", ".pytest_tmp*/", "TASKPLAN_*.md"]:
        assert pat in content, f"{pat} fehlt in .gitignore"

    for lock_pat in ["LOCK.user.*", "LOCK.until.*", "LOCK.condition.*"]:
        assert lock_pat in content, f"{lock_pat} fehlt in .gitignore"


def test_changelog_recent_pfad_a_unreleased_entry_20260930():
    """Prüft, dass CHANGELOG.md den Pfad A Hygiene-Eintrag vom 2026-09-30 unter [Unreleased] führt."""
    content = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "### Pfad A Repository Hygiene, CI Lifecycle Workflows, PEP 621 Standardisierung & Level 1 SBOM (2026-09-30) [G 2026-09-30]" in content
    assert "T-20260920-167562623" in content


def test_marketing_log_recent_pfad_a_entry_20260930():
    """Prüft, dass MARKETING-LOG.txt den Pfad A Hygiene-Eintrag vom 2026-09-30 führt."""
    content = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "2026-09-30 [HYG Pfad A] Repository Hygiene, CI Lifecycle Workflows & Level 1 SBOM:" in content
