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
    """Prüft, dass beide README-Dateien synchronisierte Badges enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    required_badges = [
        "badge/version-1.0.0-blue",
        "badge/python-3.11",
        "badge/license-GPL",
        "badge/ecosystem-dev--bricks",
        "badge/umbrella-open--bricks",
        "badge/LLM--Context-llms.txt",
    ]

    for badge in required_badges:
        assert badge in content_en, f"Badge {badge} fehlt in README.md"
        assert badge in content_de, f"Badge {badge} fehlt in README_de.md"


def test_mermaid_diagrams_present():
    """Prüft, dass beide READMEs interaktive Mermaid-Diagramme für Architektur und Datenschutz enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "```mermaid" in content_en, "README.md muss mindestens ein Mermaid-Diagramm enthalten"
    assert "```mermaid" in content_de, "README_de.md muss mindestens ein Mermaid-Diagramm enthalten"
    assert "Editor" in content_en
    assert "PyInstaller" in content_en or "Builder" in content_en
    assert "SQLite" in content_en or "FileManager" in content_en


def test_security_policy_bilingual_and_contacts():
    """Prüft, dass SECURITY.md zweisprachig ist und Zero-Egress sowie den Sicherheitskontakt enthält."""
    sec_file = REPO_ROOT / "SECURITY.md"
    assert sec_file.is_file(), "SECURITY.md fehlt im Repo-Root"

    content = sec_file.read_text(encoding="utf-8")

    assert "security@ellmos.ai" in content, "SECURITY.md muss security@ellmos.ai als Kontakt enthalten"
    assert "local-first" in content.lower(), "SECURITY.md muss local-first erwähnen"
    assert "zero-egress" in content.lower() or "offline" in content.lower()
    assert "keyring" in content.lower()
    assert "Sicherheitsrichtlinie" in content, "SECURITY.md muss einen deutschen Abschnitt enthalten"


def test_llms_txt_currency_and_structure():
    """Prüft, dass llms.txt aktuell ist, Suchphrasen und wichtige Dateireferenzen enthält."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt fehlt im Repo-Root"

    content = llms_file.read_text(encoding="utf-8")

    assert "https://github.com/dev-bricks/DevCenter" in content
    assert "2026-08-21" in content, "llms.txt Last-checked Timestamp muss auf 2026-08-21 stehen"
    assert "local-first Python IDE" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content.lower() or "umbrella" in content.lower()


def test_pyproject_version_and_ruff_config():
    """Prüft die Gültigkeit von pyproject.toml und die Linter-Konfiguration."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml fehlt im Repo-Root"

    content = pyproject_file.read_text(encoding="utf-8")

    assert 'name = "devcenter-suite"' in content
    assert 'version = "1.0.0"' in content
    assert "[tool.ruff]" in content
    assert "[tool.ruff.lint]" in content


def test_sibling_ecosystem_matrix_presence():
    """Prüft, dass beide Dokumentationen eine Ökosystem-Matrix mit dev-bricks & open-bricks enthalten."""
    content_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    content_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "dev-bricks" in content_en
    assert "open-bricks" in content_en
    assert "MethodenAnalyser" in content_en or "CodeBox" in content_en
    assert "dev-bricks" in content_de
    assert "open-bricks" in content_de


def test_changelog_currency():
    """Prüft, dass CHANGELOG.md einen aktuellen Eintrag für 2026-08-21 enthält."""
    changelog_file = REPO_ROOT / "CHANGELOG.md"
    assert changelog_file.is_file(), "CHANGELOG.md fehlt im Repo-Root"

    content = changelog_file.read_text(encoding="utf-8")
    assert "2026-08-21" in content, "CHANGELOG.md muss einen Eintrag für 2026-08-21 enthalten"
