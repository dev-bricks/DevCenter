# -*- coding: utf-8 -*-
"""
Bug-Sweep Regression Tests (2026-10-02)
Bereich: Projekt-Verwaltung, Projekt-Lifecycle und Datei-Synchronisation
(src/core/project_manager.py + src/modules/filemanager/sync_manager.py)

Bugs behoben:
1. ProjectManager: Unhandled Exceptions (AttributeError, TypeError) bei nicht-dict
   JSON-Dateien in settings.json und devcenter.json (_load_recent_projects,
   _save_recent_projects, open_project, save_project, create_project).
2. ProjectManager: Fallbacks für leere/Whitespace-Namen und Pfade in devcenter.json
   sowie Filterung ungültiger (nicht-dict) Einträge in get_recent_projects.
3. SyncManager: _should_exclude Scheitern bei Forward-Slash-Pfaden auf Windows.
4. SyncManager: _find_sqlite_databases ignorierte config.excludes und durchsuchte
   ausgeschlossene Ordner (z. B. venv, .git) bedingungslos.
5. SyncManager: verify_copy hinterließ bei Prüfsummen-Mismatch beschädigte Zieldateien
   auf der Platte, die bei Folgeläufen dauerhaft als synchronisiert galten.
6. SyncManager: sync() gab bei Nicht-Verzeichnis-Quellen Erfolg mit 0 Dateien und 0.0s zurück.
7. BackupScheduler: Fehlende Deduplizierung und Pfad-Normalisierung in add_backup.
"""

import os
import sys
import tempfile
import shutil
import json
import unittest
from pathlib import Path

# Repository root to import path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from core.project_manager import ProjectManager
from modules.filemanager.sync_manager import SyncManager, SyncConfig, BackupScheduler


class TestProjectManagerResilience(unittest.TestCase):
    """Prüft die Fehlerresilienz des ProjectManagers bei korrupten/nicht-dict JSON-Daten."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "settings.json")
        self.pm = ProjectManager(settings_path=self.settings_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_recent_projects_with_non_dict_json(self):
        """_load_recent_projects darf bei JSON-Array oder Skalaren in settings.json nicht abstürzen."""
        for invalid_json in ["[]", '"string"', "123", "null", "true"]:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                f.write(invalid_json)
            pm = ProjectManager(settings_path=self.settings_file)
            self.assertEqual(pm.recent_projects, [],
                             f"recent_projects muss bei {invalid_json} eine leere Liste sein")

    def test_save_recent_projects_with_non_dict_json(self):
        """_save_recent_projects darf bei vorherigem JSON-Array nicht mit TypeError abstürzen."""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write("[]")
        self.pm.recent_projects = [{"path": os.path.join(self.temp_dir, "p1"), "name": "P1"}]
        self.pm._save_recent_projects()

        with open(self.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertIn("recent_projects", data)
        self.assertEqual(len(data["recent_projects"]), 1)

    def test_open_project_with_non_dict_devcenter_json(self):
        """open_project muss bei devcenter.json mit Nicht-Dict-Inhalt None zurückgeben statt abzustürzen."""
        proj_dir = os.path.join(self.temp_dir, "invalid_proj")
        os.makedirs(proj_dir, exist_ok=True)
        for invalid_json in ["[]", '"not_dict"', "null", "42"]:
            devcenter_json = os.path.join(proj_dir, "devcenter.json")
            with open(devcenter_json, "w", encoding="utf-8") as f:
                f.write(invalid_json)
            res = self.pm.open_project(proj_dir)
            self.assertIsNone(res, f"open_project muss bei {invalid_json} None zurückgeben")

    def test_create_project_with_existing_non_dict_devcenter_json(self):
        """create_project muss existierende nicht-dict devcenter.json sauber überschreiben."""
        proj_dir = os.path.join(self.temp_dir, "overwrite_proj")
        os.makedirs(proj_dir, exist_ok=True)
        devcenter_json = os.path.join(proj_dir, "devcenter.json")
        with open(devcenter_json, "w", encoding="utf-8") as f:
            f.write("[]")

        cfg = self.pm.create_project(name="OverwriteTest", path=proj_dir)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.name, "OverwriteTest")
        with open(devcenter_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "OverwriteTest")

    def test_save_project_with_non_dict_devcenter_json(self):
        """save_project muss sauber funktionieren wenn devcenter.json zwischenzeitlich manipuliert wurde."""
        cfg = self.pm.create_project(name="SaveTest", path=os.path.join(self.temp_dir, "save_proj"))
        self.assertIsNotNone(cfg)
        devcenter_json = os.path.join(self.temp_dir, "save_proj", "devcenter.json")
        with open(devcenter_json, "w", encoding="utf-8") as f:
            f.write("[]")
        saved = self.pm.save_project()
        self.assertTrue(saved)
        with open(devcenter_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_get_recent_projects_ignores_malformed_entries(self):
        """get_recent_projects darf bei Nicht-Dict Elementen in recent_projects nicht crashen."""
        valid_dir = os.path.join(self.temp_dir, "valid_proj")
        os.makedirs(valid_dir, exist_ok=True)
        self.pm.recent_projects = [
            "invalid_str_entry",
            None,
            123,
            {"path": valid_dir, "name": "Valid"},
            {"path": "non_existent_path", "name": "NonExistent"}
        ]
        result = self.pm.get_recent_projects()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Valid")

    def test_open_project_empty_name_fallback(self):
        """open_project muss bei leerem oder reinem Whitespace-Namen auf den Ordnernamen zurückfallen."""
        proj_dir = os.path.join(self.temp_dir, "fallback_name_proj")
        os.makedirs(proj_dir, exist_ok=True)
        devcenter_json = os.path.join(proj_dir, "devcenter.json")
        with open(devcenter_json, "w", encoding="utf-8") as f:
            json.dump({"name": "   ", "path": ""}, f)

        cfg = self.pm.open_project(proj_dir)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.name, "fallback_name_proj")
        self.assertEqual(cfg.path, str(Path(proj_dir)))


class TestSyncManagerResilience(unittest.TestCase):
    """Prüft die Fehlerresilienz des SyncManagers bei Dateisystem- und Verifikations-Kantenfällen."""

    def setUp(self):
        self.sm = SyncManager()
        self.source_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.source_dir, ignore_errors=True)
        shutil.rmtree(self.target_dir, ignore_errors=True)

    def test_should_exclude_handles_forward_slashes_on_all_platforms(self):
        """_should_exclude muss Verzeichnis- und Dateimuster auch bei POSIX-Forward-Slashes erkennen."""
        excludes = ['__pycache__', '.git', 'venv', 'dist', '*.pyc']

        # POSIX Forward Slashes
        self.assertTrue(self.sm._should_exclude("project/venv/lib/site.py", excludes))
        self.assertTrue(self.sm._should_exclude(".git/config", excludes))
        self.assertTrue(self.sm._should_exclude("src/module/__pycache__/foo.py", excludes))
        self.assertTrue(self.sm._should_exclude("dist/app.exe", excludes))
        self.assertTrue(self.sm._should_exclude("src/file.pyc", excludes))

        # Nicht ausgeschlossene Pfade
        self.assertFalse(self.sm._should_exclude("src/module/valid.py", excludes))
        self.assertFalse(self.sm._should_exclude("project/resources/icon.png", excludes))

    def test_find_sqlite_databases_respects_excludes_and_regular_files(self):
        """_find_sqlite_databases darf ausgeschlossene Ordner (z.B. venv, .git) nicht scannen."""
        os.makedirs(os.path.join(self.source_dir, "venv", "data"), exist_ok=True)
        os.makedirs(os.path.join(self.source_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.source_dir, "dir.db"), exist_ok=True)  # Ordner mit .db Endung

        app_db = os.path.join(self.source_dir, "src", "app.db")
        venv_db = os.path.join(self.source_dir, "venv", "data", "test.sqlite")
        with open(app_db, "w", encoding="utf-8") as f:
            f.write("app database")
        with open(venv_db, "w", encoding="utf-8") as f:
            f.write("venv database")

        dbs = self.sm._find_sqlite_databases(self.source_dir, excludes=["venv"])
        self.assertIn(app_db, dbs)
        self.assertNotIn(venv_db, dbs)
        # Ordner dir.db darf nicht als SQLite-Datei erfasst werden
        self.assertNotIn(os.path.join(self.source_dir, "dir.db"), dbs)

    def test_verify_copy_cleans_up_corrupted_target_file(self):
        """verify_copy muss beschädigte Zieldateien bei Hash-Mismatch sofort entfernen."""
        src_file = os.path.join(self.source_dir, "data.bin")
        with open(src_file, "wb") as f:
            f.write(b"Original Valid Data")

        cfg = SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir,
            verify_copy=True,
            checkpoint_sqlite=False
        )

        orig_hash_fn = self.sm._get_file_hash

        def fake_mismatch_hash(path):
            if "data.bin" in path and self.target_dir in path:
                return "mismatch_hash_abc"
            return orig_hash_fn(path)

        self.sm._get_file_hash = fake_mismatch_hash

        result = self.sm.sync(cfg)
        target_file = Path(self.target_dir) / "data.bin"

        self.assertFalse(result.success)
        self.assertTrue(any("Verifikation fehlgeschlagen" in err for err in result.errors))
        self.assertFalse(target_file.exists(),
                         "Beschädigte Zieldatei muss nach Verifikationsfehler vom Ziel gelöscht werden")
        self.assertEqual(result.files_copied, 0, "Fehlgeschlagene Dateien dürfen nicht als kopiert zählen")

    def test_sync_rejects_non_directory_source(self):
        """sync() muss abbrechen und Fehler melden, wenn source_path kein Verzeichnis ist."""
        file_path = os.path.join(self.source_dir, "single_file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("not a directory")

        cfg = SyncConfig(source_path=file_path, target_path=self.target_dir)
        result = self.sm.sync(cfg)

        self.assertFalse(result.success)
        self.assertTrue(any("kein Verzeichnis" in err for err in result.errors))
        self.assertGreaterEqual(result.duration, 0.0)

    def test_backup_scheduler_deduplicates_and_normalizes_project(self):
        """BackupScheduler.add_backup muss bestehende Projekteinträge aktualisieren statt zu duplizieren."""
        scheduler = BackupScheduler(self.sm)
        p1 = os.path.join(self.source_dir, "my_project")
        b1 = os.path.join(self.target_dir, "backup1")
        b2 = os.path.join(self.target_dir, "backup2")

        scheduler.add_backup(p1, b1, interval_minutes=60)
        self.assertEqual(len(scheduler.backup_configs), 1)

        # Mit Trailing-Slash oder redundanten Pfadtrennern erneut hinzufügen
        scheduler.add_backup(p1 + os.sep, b2, interval_minutes=120)
        self.assertEqual(len(scheduler.backup_configs), 1,
                         "Gleicher Pfad darf nicht doppelt in backup_configs eingetragen werden")
        self.assertEqual(scheduler.backup_configs[0]["backup"], b2)
        self.assertEqual(scheduler.backup_configs[0]["interval"], 120)

        # remove_backup mit normalisiertem Pfad
        scheduler.remove_backup(p1 + os.sep)
        self.assertEqual(len(scheduler.backup_configs), 0)


if __name__ == "__main__":
    unittest.main()
