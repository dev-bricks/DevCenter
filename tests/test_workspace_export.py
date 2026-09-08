# -*- coding: utf-8 -*-
"""Tests für den redigierten DevCenter-Workspace-Export."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.project_manager import ProjectConfig
from core.settings_manager import SettingsManager
from core.workspace_export import build_workspace_export, export_workspace


class WorkspaceExportTests(unittest.TestCase):
    """Deckt Schema, Redaktionen und offene Aufgaben ab."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.project_root = Path(self.temp_dir.name) / "DemoProject"
        (self.project_root / "src").mkdir(parents=True)
        (self.project_root / "resources").mkdir()

        (self.project_root / "src" / "main.py").write_text(
            "print('hello')\n",
            encoding="utf-8",
        )
        (self.project_root / "requirements.txt").write_text(
            "PySide6>=6.5.0\npyinstaller>=5.0\nanthropic>=0.18.0\n",
            encoding="utf-8",
        )
        (self.project_root / "AUFGABEN.txt").write_text(
            "# Aufgaben\n\n"
            "## PORTIERUNG / PLATTFORMÜBERGREIFENDE NUTZUNG (2026-05-27)\n"
            "[ ] P0: Exportvertrag finalisieren\n"
            "[ ] P2: Desktop-Export umsetzen\n"
            "[x] Bereits erledigt\n",
            encoding="utf-8",
        )
        (self.project_root / "devcenter.json").write_text(
            json.dumps(
                {
                    "name": "DemoProject",
                    "path": str(self.project_root),
                    "created": "2026-06-01T00:00:00",
                    "last_opened": "2026-06-01T00:00:00",
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.settings_path = Path(self.temp_dir.name) / "settings.json"
        self.settings = SettingsManager(str(self.settings_path))
        self.settings.set("ai.api_key", "super-secret-token")
        self.settings.set("sync.backup_path", r"C:\Users\User\Backups\DevCenter")
        self.settings.set("build.default_output_dir", r"C:\Users\User\Builds\DevCenter")

        self.project = ProjectConfig(
            name="DemoProject",
            path=str(self.project_root),
            created="2026-06-01T00:00:00",
            last_opened="2026-06-01T00:00:00",
            main_file="src/main.py",
            description="Lokales Python-Testprojekt",
            version="1.2.3",
            build_config={
                "output_dir": r"C:\Users\User\Builds\DevCenter",
                "one_file": False,
                "console": True,
                "icon": str(self.project_root / "resources" / "app.ico"),
            },
        )
        (self.project_root / "resources" / "app.ico").write_text("ico", encoding="utf-8")

        self.problems = [
            SimpleNamespace(
                severity=SimpleNamespace(value="warning"),
                message="TODO im Projekt gefunden",
                file_path=str(self.project_root / "src" / "main.py"),
                line=1,
                column=1,
                source="analyzer",
                code="TODO001",
            )
        ]

    def test_build_workspace_export_redacts_secrets_and_paths(self):
        payload = build_workspace_export(
            self.project,
            self.settings,
            problems=self.problems,
            exported_at=datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc),
        )

        dump = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["schema"], "devcenter-workspace-v1")
        self.assertEqual(payload["project"]["path_ref"], "project-1")
        self.assertEqual(payload["project"]["main_file_ref"], "project-1/src/main.py")
        self.assertIn("PySide6", payload["project"]["frameworks"])
        self.assertEqual(payload["analysis"]["summary"]["problems_total"], 1)
        self.assertEqual(payload["analysis"]["problems"][0]["file_ref"], "project-1/src/main.py")
        self.assertEqual(payload["build"]["output_ref"], "output-dir-1")
        self.assertEqual(payload["build"]["icon_ref"], "project-1/resources/app.ico")
        self.assertEqual(payload["tasks"][0]["priority"], "P0")
        self.assertEqual(payload["release"]["checklists"][0]["title"], "Exportvertrag finalisieren")
        self.assertNotIn("super-secret-token", dump)
        self.assertNotIn(r"C:\Users\User", dump)

    def test_count_project_files_ignores_ignored_dirs(self):
        """_count_project_files darf keine Dateien in build/, dist/ usw. zählen."""
        from core.workspace_export import _count_project_files

        build_dir = self.project_root / "build" / "myapp"
        build_dir.mkdir(parents=True)
        (build_dir / "myapp.exe").write_text("binary", encoding="utf-8")

        count = _count_project_files(self.project_root)
        all_files = list(self.project_root.rglob("*"))
        total_files = sum(1 for p in all_files if p.is_file())

        self.assertLess(count, total_files, "Dateien in build/ müssen ausgeschlossen werden")

    def test_count_project_files_does_not_exclude_project_inside_build_parent(self):
        """_count_project_files darf Projektdateien nicht ausschließen, wenn der Projektpfad 'build' enthält."""
        from core.workspace_export import _count_project_files
        import tempfile

        with tempfile.TemporaryDirectory() as build_root:
            project_dir = Path(build_root) / "build" / "my_project"
            (project_dir / "src").mkdir(parents=True)
            (project_dir / "src" / "main.py").write_text("print('hi')", encoding="utf-8")

            count = _count_project_files(project_dir)
            self.assertEqual(count, 1, "main.py muss gezählt werden, obwohl Elternpfad 'build' heißt")

    def test_export_workspace_writes_utf8_without_bom(self):
        output_path = self.project_root / "workspace-export.json"
        export_workspace(
            self.project,
            self.settings,
            str(output_path),
            problems=self.problems,
        )

        raw = output_path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))

        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(payload["schema"], "devcenter-workspace-v1")
        self.assertEqual(payload["build"]["output_ref"], "output-dir-1")

    def test_build_workspace_export_includes_hidden_imports(self):
        """Regression: build_workspace_export() muss hidden_imports aus der Build-Konfiguration übernehmen."""
        self.project.build_config["hidden_imports"] = ["pkg_resources.py2_warn", "chardet"]
        payload = build_workspace_export(
            self.project,
            self.settings,
            problems=self.problems,
            exported_at=datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(payload["build"]["hidden_imports"], ["pkg_resources.py2_warn", "chardet"])

    def test_parse_open_tasks_standard_markdown_lists(self):
        """Regression B-005: _parse_open_tasks muss Standard-Markdown-Listen (- [ ], * [ ], + [ ]) erfassen."""
        from core.workspace_export import _parse_open_tasks

        tasks_file = self.project_root / "AUFGABEN_TEST.txt"
        tasks_file.write_text(
            "# Projekt-Aufgaben\n\n"
            "## PORTIERUNG / PLATTFORMÜBERGREIFENDE NUTZUNG (2026-05-27)\n"
            "- [ ] P0: Dash-Listen-Aufgabe\n"
            "* [ ] P1: Asterisk-Listen-Aufgabe\n"
            "+ [ ] P2: Plus-Listen-Aufgabe\n"
            "  - [ ] P0: Eingerückte Aufgabe\n"
            "[ ] P3: Bare-Checkbox-Aufgabe\n"
            "- [x] Erledigte Dash-Aufgabe\n"
            "* [x] Erledigte Asterisk-Aufgabe\n"
            "[x] Erledigte Bare-Aufgabe\n",
            encoding="utf-8",
        )

        tasks = _parse_open_tasks(tasks_file)
        self.assertEqual(len(tasks), 5, "Genau 5 offene Aufgaben müssen geparst werden")
        self.assertEqual(tasks[0]["priority"], "P0")
        self.assertEqual(tasks[0]["title"], "Dash-Listen-Aufgabe")
        self.assertEqual(tasks[1]["priority"], "P1")
        self.assertEqual(tasks[1]["title"], "Asterisk-Listen-Aufgabe")
        self.assertEqual(tasks[2]["priority"], "P2")
        self.assertEqual(tasks[2]["title"], "Plus-Listen-Aufgabe")
        self.assertEqual(tasks[3]["priority"], "P0")
        self.assertEqual(tasks[3]["title"], "Eingerückte Aufgabe")
        self.assertEqual(tasks[4]["priority"], "P3")
        self.assertEqual(tasks[4]["title"], "Bare-Checkbox-Aufgabe")

    def test_parse_requirements_supports_pep508_extras_and_markers(self):
        """Regression B-006: _parse_requirements muss PEP-508 Extras und Environment-Marker parsen."""
        from core.workspace_export import _parse_requirements

        req_file = self.project_root / "req_test.txt"
        req_file.write_text(
            "# Kommentarzeile\n"
            "requests[security]>=2.28.0\n"
            "pydantic[email,dotenv]>=2.0.0 # inline comment\n"
            "uvicorn[standard]\n"
            "importlib-metadata>=4.4;python_version<'3.10'\n"
            "PySide6>=6.5.0\n",
            encoding="utf-8",
        )

        reqs = _parse_requirements(req_file)
        self.assertEqual(len(reqs), 5)
        self.assertEqual(reqs[0]["name"], "requests")
        self.assertEqual(reqs[0]["extras"], ["security"])
        self.assertEqual(reqs[0]["specifier"], ">=2.28.0")

        self.assertEqual(reqs[1]["name"], "pydantic")
        self.assertEqual(reqs[1]["extras"], ["email", "dotenv"])
        self.assertEqual(reqs[1]["specifier"], ">=2.0.0")

        self.assertEqual(reqs[2]["name"], "uvicorn")
        self.assertEqual(reqs[2]["extras"], ["standard"])
        self.assertNotIn("specifier", reqs[2])

        self.assertEqual(reqs[3]["name"], "importlib-metadata")
        self.assertEqual(reqs[3]["specifier"], ">=4.4")

        self.assertEqual(reqs[4]["name"], "PySide6")
        self.assertNotIn("extras", reqs[4])
        self.assertEqual(reqs[4]["specifier"], ">=6.5.0")

    def test_count_project_files_prunes_venv_node_modules_and_caches(self):
        """Regression B-007: _count_project_files muss .venv, node_modules, .ruff_cache etc. ignorieren."""
        from core.workspace_export import _count_project_files

        venv_dir = self.project_root / ".venv" / "Lib" / "site-packages"
        venv_dir.mkdir(parents=True)
        (venv_dir / "dummy.py").write_text("pass", encoding="utf-8")

        node_dir = self.project_root / "node_modules" / "express"
        node_dir.mkdir(parents=True)
        (node_dir / "index.js").write_text("console.log()", encoding="utf-8")

        ruff_dir = self.project_root / ".ruff_cache" / "content"
        ruff_dir.mkdir(parents=True)
        (ruff_dir / "cache.json").write_text("{}", encoding="utf-8")

        # In setUp wurden angelegt: src/main.py, requirements.txt, AUFGABEN.txt, devcenter.json, resources/app.ico (5 Dateien)
        # Die 3 Dateien in .venv, node_modules und .ruff_cache müssen ignoriert werden.
        count = _count_project_files(self.project_root)
        self.assertEqual(count, 5, "Nur die 5 echten Projektdateien dürfen gezählt werden, keine aus .venv/node_modules/.ruff_cache")

    def test_infer_frameworks_preserves_pure_pyqt6(self):
        """Regression B-008: _infer_frameworks darf bei reinen PyQt6-Projekten PySide6 nicht erzwingen."""
        from core.workspace_export import _infer_frameworks

        # Reines PyQt6 Projekt
        pyqt_reqs = [{"name": "PyQt6", "specifier": ">=6.5.0"}]
        frameworks = _infer_frameworks(pyqt_reqs)
        self.assertEqual(frameworks, ["PyQt6"], "PySide6 darf bei reinem PyQt6 nicht hinzugefügt werden")

        # PySide6 Projekt
        pyside_reqs = [{"name": "PySide6", "specifier": ">=6.5.0"}]
        frameworks = _infer_frameworks(pyside_reqs)
        self.assertEqual(frameworks, ["PySide6"])

        # Projekt ohne Qt (Fallback auf PySide6)
        other_reqs = [{"name": "anthropic", "specifier": ">=0.18.0"}]
        frameworks = _infer_frameworks(other_reqs)
        self.assertEqual(frameworks, ["PySide6", "Anthropic"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
