# -*- coding: utf-8 -*-
"""
DevCenter - Unit Tests
Testet die Kernkomponenten
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Pfad für Imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestProjectManager(unittest.TestCase):
    """Tests für ProjectManager"""
    
    def setUp(self):
        """Erstellt temporäres Verzeichnis"""
        self.temp_dir = tempfile.mkdtemp()
        from core.project_manager import ProjectManager
        self.settings_file = os.path.join(self.temp_dir, "settings.json")
        self.pm = ProjectManager(settings_path=self.settings_file)
    
    def tearDown(self):
        """Räumt auf"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_project(self):
        """Testet Projekt-Erstellung"""
        project = self.pm.create_project(
            name="TestProject",
            path=self.temp_dir
        )
        
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "TestProject")
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "devcenter.json")))
    
    def test_open_project(self):
        """Testet Projekt-Öffnen"""
        # Erst erstellen
        self.pm.create_project("Test", self.temp_dir)
        
        # Dann öffnen
        project = self.pm.open_project(self.temp_dir)
        
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "Test")
    
    def test_recent_projects(self):
        """Testet Recent-Projects-Liste"""
        self.pm.create_project("Test1", self.temp_dir)

        recent = self.pm.get_recent_projects()
        self.assertTrue(len(recent) >= 1)

    def test_create_project_template_files_have_real_newlines(self):
        """_create_template_files darf kein literales \\n in Template-Dateien schreiben."""
        project_dir = os.path.join(self.temp_dir, "newline_test")
        os.makedirs(project_dir, exist_ok=True)
        self.pm.create_project("NewlineTest", project_dir)
        init_path = os.path.join(project_dir, "src", "__init__.py")
        req_path = os.path.join(project_dir, "requirements.txt")
        for path in (init_path, req_path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("\\n", content,
                             f"{path} enthält literales \\\\n statt echtem Newline")

    def test_save_recent_projects_handles_corrupt_settings_json(self):
        """_save_recent_projects muss json.JSONDecodeError sauber abfangen."""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write("{ not valid json }")

        project_dir = os.path.join(self.temp_dir, "new_project")
        os.makedirs(project_dir, exist_ok=True)
        result = self.pm.create_project("CorruptSettingsTest", project_dir)
        self.assertIsNotNone(result, "create_project muss trotz korrupter settings.json funktionieren")

    def test_get_recent_projects_emits_signal_on_stale_cleanup(self):
        """Regression: get_recent_projects() muss recent_projects_changed emittieren wenn
        veraltete Einträge entfernt werden — ohne Fix bleibt die UI-Darstellung der Liste veraltet."""
        import inspect
        from core.project_manager import ProjectManager
        source = inspect.getsource(ProjectManager.get_recent_projects)
        self.assertIn('recent_projects_changed.emit', source,
                      "get_recent_projects() muss recent_projects_changed emittieren wenn veraltete Einträge entfernt wurden")


class TestSettingsManager(unittest.TestCase):
    """Tests für SettingsManager"""
    
    def setUp(self):
        from core.settings_manager import SettingsManager
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "settings.json")
        self.sm = SettingsManager(self.settings_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_default(self):
        """Testet Default-Wert"""
        value = self.sm.get('nonexistent.key', 'default')
        self.assertEqual(value, 'default')
    
    def test_set_and_get(self):
        """Testet Setzen und Lesen"""
        self.sm.set('test.key', 'test_value')
        value = self.sm.get('test.key')
        self.assertEqual(value, 'test_value')
    
    def test_nested_keys(self):
        """Testet verschachtelte Schlüssel"""
        self.sm.set('level1.level2.level3', 42)
        value = self.sm.get('level1.level2.level3')
        self.assertEqual(value, 42)

    def test_extra_keys_persist(self):
        """Testet Persistenz nicht modellierter Schlüssel"""
        from core.settings_manager import SettingsManager

        self.sm.set('build.output_dir', 'custom_dist')
        self.sm.set('level1.level2.level3', 42)

        reloaded = SettingsManager(self.settings_file)

        self.assertEqual(reloaded.get('build.output_dir'), 'custom_dist')
        self.assertEqual(reloaded.get('level1.level2.level3'), 42)


class TestEventBus(unittest.TestCase):
    """Tests für EventBus"""
    
    def setUp(self):
        from core.event_bus import EventBus, EventType
        self.eb = EventBus()
        self.EventType = EventType
        self.received_events = []
    
    def test_subscribe_and_emit(self):
        """Testet Subscribe und Emit"""
        def handler(event):
            self.received_events.append(event)
        
        self.eb.subscribe(self.EventType.FILE_OPENED, handler)
        self.eb.emit(self.EventType.FILE_OPENED, {'path': 'test.py'})
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].data['path'], 'test.py')
    
    def test_unsubscribe(self):
        """Testet Unsubscribe"""
        def handler(event):
            self.received_events.append(event)
        
        self.eb.subscribe(self.EventType.FILE_SAVED, handler)
        self.eb.unsubscribe(self.EventType.FILE_SAVED, handler)
        self.eb.emit(self.EventType.FILE_SAVED, {})
        
        self.assertEqual(len(self.received_events), 0)


class TestMethodAnalyzer(unittest.TestCase):
    """Tests für MethodAnalyzer"""
    
    def setUp(self):
        from modules.analyzer import MethodAnalyzer
        self.analyzer = MethodAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_simple_file(self):
        """Testet Analyse einer einfachen Datei"""
        code = '''
def hello():
    """Says hello"""
    print("Hello, World!")

class Greeter:
    def greet(self, name):
        return f"Hello, {name}!"
'''
        
        file_path = os.path.join(self.temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = self.analyzer.analyze_file(file_path)
        
        self.assertEqual(len(result.functions), 1)
        self.assertEqual(result.functions[0].name, 'hello')
        self.assertEqual(len(result.classes), 1)
        self.assertEqual(result.classes[0].name, 'Greeter')
    
    def test_syntax_error_detection(self):
        """Testet Erkennung von Syntax-Fehlern"""
        code = '''
def broken(:
    pass
'''
        
        file_path = os.path.join(self.temp_dir, "broken.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = self.analyzer.analyze_file(file_path)
        
        self.assertTrue(len(result.errors) > 0)
        self.assertEqual(result.errors[0]['type'], 'SyntaxError')
    
    def test_complexity_calculation(self):
        """Testet Komplexitäts-Berechnung"""
        code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
            else:
                print(-i)
    else:
        while x < 0:
            x += 1
    return x
'''

        file_path = os.path.join(self.temp_dir, "complex.py")
        with open(file_path, 'w') as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)

        self.assertTrue(result.functions[0].complexity > 1)

    def test_aliased_from_import_not_flagged_as_unused(self):
        """Bug 19: from X import Y as Z darf nicht als ungenutzt gelten wenn Z verwendet wird."""
        code = 'from typing import Optional as Opt\ndef f(x: Opt) -> None:\n    pass\n'
        file_path = os.path.join(self.temp_dir, "aliased.py")
        with open(file_path, 'w') as f:
            f.write(code)
        result = self.analyzer.analyze_file(file_path)
        self.assertNotIn('typing.Optional', result.unused_imports,
                         "Aliasierter From-Import fälschlich als ungenutzt markiert")


class TestKompilator(unittest.TestCase):
    """Tests für Kompilator"""

    def test_pyinstaller_check(self):
        """Testet PyInstaller-Verfügbarkeit"""
        from modules.builder import Kompilator

        kompilator = Kompilator()
        # Sollte nicht abstürzen
        available = kompilator.check_pyinstaller()
        self.assertIsInstance(available, bool)

    def test_build_resolves_output_dir_relative_to_script_dir(self):
        """build() muss output_dir relativ zum Skript-Verzeichnis auflösen, nicht Python-CWD."""
        import inspect
        from modules.builder import Kompilator
        source = inspect.getsource(Kompilator.build)
        self.assertIn('isabs', source, "build() muss prüfen ob output_dir absolut ist")
        self.assertIn('abspath', source, "build() muss den absoluten Skript-Verzeichnis-Pfad verwenden")

    def test_clean_build_uses_script_directory(self):
        """_clean_build muss Artefakte relativ zum Skript-Verzeichnis löschen."""
        from modules.builder import Kompilator, BuildConfig

        kompilator = Kompilator()
        temp_dir = tempfile.mkdtemp()
        try:
            script_path = os.path.join(temp_dir, "myscript.py")
            open(script_path, "w").close()

            # Fake Build-Artefakte im Skript-Verzeichnis anlegen
            build_dir = os.path.join(temp_dir, "build", "myscript")
            os.makedirs(build_dir)
            spec_file = os.path.join(temp_dir, "myscript.spec")
            with open(spec_file, "w") as f:
                f.write("# dummy spec")

            config = BuildConfig(script_path=script_path, name="myscript")
            # Aufruf aus einem anderen Arbeitsverzeichnis simulieren
            original_cwd = os.getcwd()
            try:
                os.chdir(self.temp_dir if hasattr(self, "temp_dir") else tempfile.gettempdir())
                kompilator._clean_build(config)
            finally:
                os.chdir(original_cwd)

            self.assertFalse(os.path.exists(build_dir), "build/<name>-Ordner wurde nicht gelöscht")
            self.assertFalse(os.path.exists(spec_file), ".spec-Datei wurde nicht gelöscht")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestSyncManager(unittest.TestCase):
    """Tests für SyncManager"""
    
    def setUp(self):
        from modules.filemanager import SyncManager, SyncConfig
        self.sm = SyncManager()
        self.SyncConfig = SyncConfig
        self.source_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.source_dir, ignore_errors=True)
        shutil.rmtree(self.target_dir, ignore_errors=True)
    
    def test_sync_files(self):
        """Testet Datei-Synchronisation"""
        # Dateien erstellen
        with open(os.path.join(self.source_dir, "test.txt"), 'w') as f:
            f.write("Hello")
        
        config = self.SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir
        )
        
        result = self.sm.sync(config)
        
        self.assertTrue(result.success)
        self.assertEqual(result.files_copied, 1)
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "test.txt")))
    
    def test_exclude_patterns(self):
        """Testet Ausschluss-Muster"""
        # Dateien erstellen
        with open(os.path.join(self.source_dir, "include.txt"), 'w') as f:
            f.write("Include")

        os.makedirs(os.path.join(self.source_dir, "__pycache__"))
        with open(os.path.join(self.source_dir, "__pycache__", "cache.pyc"), 'w') as f:
            f.write("Cache")

        config = self.SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir,
            excludes=['__pycache__']
        )

        result = self.sm.sync(config)

        self.assertTrue(result.success)
        self.assertFalse(os.path.exists(os.path.join(self.target_dir, "__pycache__")))

    def test_cancelled_sync_reports_failure(self):
        """sync() muss nach Abbruch während der Kopierphase success=False melden."""
        import inspect
        from modules.filemanager.sync_manager import SyncManager
        source = inspect.getsource(SyncManager.sync)
        self.assertEqual(source.count('Sync abgebrochen'), 2,
                         "sync() muss 'Sync abgebrochen' sowohl bei frühem als auch spätem Cancel eintragen")

    def test_delete_orphans_respects_excludes(self):
        """delete_orphans darf Dateien in ausgeschlossenen Verzeichnissen nicht löschen."""
        from modules.filemanager import SyncConfig

        # Quelldatei
        with open(os.path.join(self.source_dir, "keep.txt"), "w") as f:
            f.write("keep")

        # Erste Synchronisation
        config = SyncConfig(source_path=self.source_dir, target_path=self.target_dir)
        self.sm.sync(config)

        # Im Ziel ein ausgeschlossenes Verzeichnis anlegen (simuliert .git etc.)
        excluded_dir = os.path.join(self.target_dir, "__pycache__")
        os.makedirs(excluded_dir)
        excluded_file = os.path.join(excluded_dir, "cached.pyc")
        with open(excluded_file, "w") as f:
            f.write("cache")

        # Zweite Sync mit delete_orphans=True
        config2 = SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir,
            excludes=["__pycache__"],
            delete_orphans=True,
        )
        result = self.sm.sync(config2)

        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(excluded_file), "Ausgeschlossene Datei wurde fälschlich gelöscht")

    def test_delete_orphan_error_includes_exception_detail(self):
        """Regression: Fehlertext beim Löschen einer Waisendatei muss die Exception enthalten.
        Ohne Fix: f'Löschen fehlgeschlagen: {rel_path}' — Exception-Grund fehlt komplett."""
        from unittest.mock import patch
        from modules.filemanager import SyncConfig

        # Datei im Ziel anlegen (kein Pendant in der Quelle → Waisendatei)
        orphan_path = os.path.join(self.target_dir, "orphan.txt")
        with open(orphan_path, "w") as f:
            f.write("orphan")

        config = SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir,
            delete_orphans=True,
        )

        with patch("os.remove", side_effect=PermissionError("Zugriff verweigert")):
            result = self.sm.sync(config)

        self.assertTrue(any("Zugriff verweigert" in e for e in result.errors),
                        f"Fehlermeldung muss Exception-Text enthalten; errors={result.errors}")


class TestEventBusUnsubscribeDuringEmit(unittest.TestCase):
    """EventBus: Callback darf sich während Emission selbst abmelden."""

    def test_unsubscribe_during_emit_does_not_skip_next(self):
        from core.event_bus import EventBus, EventType
        import sys
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)

        bus = EventBus()
        results = []

        def cb_a(event):
            results.append('A')
            bus.unsubscribe(EventType.FILE_OPENED, cb_a)

        def cb_b(event):
            results.append('B')

        bus.subscribe(EventType.FILE_OPENED, cb_a)
        bus.subscribe(EventType.FILE_OPENED, cb_b)
        bus.emit(EventType.FILE_OPENED)

        self.assertIn('B', results, "cb_b darf nicht übersprungen werden wenn cb_a sich abmeldet")


class TestEncodingFixer(unittest.TestCase):
    """Tests für EncodingFixer"""
    
    def setUp(self):
        from modules.analyzer import EncodingFixer
        self.fixer = EncodingFixer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_utf8(self):
        """Testet UTF-8 Erkennung"""
        file_path = os.path.join(self.temp_dir, "utf8.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello Wörld! 你好")
        
        encoding, confidence = self.fixer.detect_encoding(file_path)
        
        self.assertIn('utf', encoding.lower())
    
    def test_check_file(self):
        """Testet Datei-Prüfung"""
        file_path = os.path.join(self.temp_dir, "test.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Test content")
        
        result = self.fixer.check_file(file_path)
        
        self.assertTrue(result['is_valid_utf8'])


class TestAIService(unittest.TestCase):
    """Tests für AIService"""
    
    def test_service_without_key(self):
        """Testet Service ohne API-Key"""
        from modules.ai_assistant import AIService
        
        service = AIService(api_key="")
        
        self.assertFalse(service.is_available())
    
    def test_model_setting(self):
        """Testet Modell-Einstellung"""
        from modules.ai_assistant import AIService, AIModel

        service = AIService()
        service.set_model(AIModel.CLAUDE_OPUS)

        self.assertEqual(service.model, AIModel.CLAUDE_OPUS.value)

    def test_ai_worker_loop_cleanup_in_source(self):
        """AIWorker.run() muss event loop in finally schließen, sonst Leak bei Exception."""
        import inspect
        from gui.panels.ai_panel import AIWorker
        source = inspect.getsource(AIWorker.run)
        self.assertIn('finally', source, "AIWorker.run() muss finally-Block für loop.close() haben")
        self.assertIn('loop.close()', source, "AIWorker.run() muss loop.close() in finally aufrufen")


class TestProfilerBridge(unittest.TestCase):
    """Tests für ProfilerBridge"""
    
    def setUp(self):
        from modules.filemanager import ProfilerBridge
        self.temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.temp_dir, "test_index.db")
        self.bridge = ProfilerBridge(db_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_index_file(self):
        """Testet Datei-Indizierung"""
        file_path = os.path.join(self.temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write("print('Hello')")
        
        success = self.bridge.index_file(file_path)
        
        self.assertTrue(success)
    
    def test_search(self):
        """Testet Suche"""
        file_path = os.path.join(self.temp_dir, "searchable.py")
        with open(file_path, 'w') as f:
            f.write("def unique_function_name():\n    pass")

        self.bridge.index_file(file_path)
        results = self.bridge.search("unique_function_name")

        self.assertTrue(len(results) > 0)

    def test_index_directory_does_not_exclude_file_with_excluded_word_in_name(self):
        """index_directory darf Dateien wie build_helper.py nicht wegen Substring 'build' ausschließen."""
        project_dir = os.path.join(self.temp_dir, "my_project")
        os.makedirs(project_dir)
        build_helper = os.path.join(project_dir, "build_helper.py")
        with open(build_helper, "w") as f:
            f.write("# helper")

        count = self.bridge.index_directory(project_dir)
        self.assertEqual(count, 1, "build_helper.py muss indiziert werden, da es nicht in build/ liegt")

    def test_find_duplicates_with_apostrophe_in_project_path(self):
        """find_duplicates darf bei Apostroph im project_path nicht abstürzen."""
        project_path = "/Users/O'Brien/MyProject"
        # Soll keinen OperationalError werfen
        try:
            result = self.bridge.find_duplicates(project_path=project_path)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.fail(f"find_duplicates mit Apostroph-Pfad crashte: {e}")

    def test_get_statistics_with_apostrophe_in_project_path(self):
        """get_statistics darf bei Apostroph im project_path nicht abstürzen."""
        project_path = "/Users/O'Brien/MyProject"
        try:
            stats = self.bridge.get_statistics(project_path=project_path)
            self.assertEqual(stats['total_files'], 0)
        except Exception as e:
            self.fail(f"get_statistics mit Apostroph-Pfad crashte: {e}")

    def test_fts_search_respects_project_path_filter(self):
        """Bug 20: FTS-Suche darf bei project_path-Filter keine Treffer aus anderen Projekten zurückgeben."""
        project_a = os.path.join(self.temp_dir, "proj_a")
        project_b = os.path.join(self.temp_dir, "proj_b")
        os.makedirs(project_a)
        os.makedirs(project_b)

        file_a = os.path.join(project_a, "alpha.py")
        file_b = os.path.join(project_b, "beta.py")
        with open(file_a, 'w') as f:
            f.write("def unique_alpha_xyz(): pass")
        with open(file_b, 'w') as f:
            f.write("def unique_alpha_xyz(): pass")

        self.bridge.index_file(file_a, project_path=project_a)
        self.bridge.index_file(file_b, project_path=project_b)

        results = self.bridge.search("unique_alpha_xyz", project_path=project_a)
        for r in results:
            self.assertEqual(r.file.path, file_a,
                             f"FTS lieferte Ergebnis aus falschem Projekt: {r.file.path}")

    def test_search_closes_connection_on_exception(self):
        """Bug 40: search() muss conn.close() auch bei DB-Fehler aufrufen (kein Connection-Leak)."""
        from unittest.mock import MagicMock, patch

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("injected DB error")
        mock_conn.cursor.return_value = mock_cursor

        with patch("modules.filemanager.profiler_bridge.sqlite3.connect", return_value=mock_conn):
            result = self.bridge.search("anything")

        mock_conn.close.assert_called_once()
        self.assertEqual(result, [])

    def test_get_statistics_closes_connection_on_exception(self):
        """Bug 40: get_statistics() muss conn.close() auch bei DB-Fehler aufrufen."""
        from unittest.mock import MagicMock, patch

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("injected DB error")
        mock_conn.cursor.return_value = mock_cursor

        with patch("modules.filemanager.profiler_bridge.sqlite3.connect", return_value=mock_conn):
            stats = self.bridge.get_statistics()

        mock_conn.close.assert_called_once()
        self.assertEqual(stats['total_files'], 0)


class TestSettingsDialogPersistence(unittest.TestCase):
    """Statischer Test: SettingsDialog muss alle UI-Felder speichern und laden."""

    def test_ai_model_is_saved_and_loaded(self):
        """ai.model-Auswahl muss in _save_settings und _load_settings vorkommen."""
        import inspect
        from gui.dialogs.settings_dialog import SettingsDialog
        save_src = inspect.getsource(SettingsDialog._save_settings)
        load_src = inspect.getsource(SettingsDialog._load_settings)
        self.assertIn('ai.model', save_src, "_save_settings muss ai.model speichern")
        self.assertIn('ai.model', load_src, "_load_settings muss ai.model laden")

    def test_backup_interval_is_saved_and_loaded(self):
        """sync.backup_interval_minutes muss in _save_settings und _load_settings vorkommen."""
        import inspect
        from gui.dialogs.settings_dialog import SettingsDialog
        save_src = inspect.getsource(SettingsDialog._save_settings)
        load_src = inspect.getsource(SettingsDialog._load_settings)
        self.assertIn('backup_interval', save_src, "_save_settings muss backup_interval speichern")
        self.assertIn('backup_interval', load_src, "_load_settings muss backup_interval laden")


class TestBuildSettingsKeyNames(unittest.TestCase):
    """SettingsDialog muss die kanonischen BuildSettings-Feldnamen verwenden."""

    def test_build_settings_uses_canonical_field_names(self):
        """build.output_dir/console/upx sind keine gültigen Felder — canonical ist
        default_output_dir / console_mode / upx_enabled."""
        import inspect
        from gui.dialogs.settings_dialog import SettingsDialog
        src = inspect.getsource(SettingsDialog._load_settings) + \
              inspect.getsource(SettingsDialog._save_settings)
        self.assertIn('default_output_dir', src,
                      "_load/_save muss 'build.default_output_dir' verwenden")
        self.assertIn('console_mode', src,
                      "_load/_save muss 'build.console_mode' verwenden")
        self.assertIn('upx_enabled', src,
                      "_load/_save muss 'build.upx_enabled' verwenden")
        self.assertNotIn("'build.output_dir'", src,
                         "_load/_save darf nicht den falschen Key 'build.output_dir' verwenden")
        self.assertNotIn("'build.console'", src,
                         "_load/_save darf nicht den falschen Key 'build.console' verwenden")
        self.assertNotIn("'build.upx'", src,
                         "_load/_save darf nicht den falschen Key 'build.upx' verwenden")


class TestBuildDialogImport(unittest.TestCase):
    """BuildDialog muss den Builder mit absolutem Import laden (nicht mit 3 Punkten)."""

    def test_build_dialog_uses_absolute_import_for_builder(self):
        """'from ...modules.builder' scheitert immer — nur absoluter Import funktioniert."""
        import inspect
        from gui.dialogs.build_dialog import BuildDialog
        source = inspect.getsource(BuildDialog._start_build)
        self.assertNotIn('from ...modules.builder', source,
                         "_start_build darf keinen 3-Punkte-Relativ-Import verwenden")
        self.assertIn('from modules.builder', source,
                      "_start_build muss 'from modules.builder' (absolut) verwenden")


class TestNewProjectDialogValidation(unittest.TestCase):
    """Statischer Test: NewProjectDialog muss leere safe_names ablehnen."""

    def test_validate_and_accept_rejects_empty_safe_name(self):
        """Namen aus nur Sonderzeichen erzeugen leere safe_name → darf nicht akzeptiert werden."""
        import inspect
        from gui.dialogs.new_project_dialog import NewProjectDialog
        source = inspect.getsource(NewProjectDialog._validate_and_accept)
        self.assertIn('not safe_name', source,
                      "_validate_and_accept muss empty safe_name ablehnen")


class TestAIPanelInlineCodeEscaping(unittest.TestCase):
    """Statischer Test: Inline-Code-Blöcke in _format_code_blocks müssen HTML-escaped werden."""

    def test_inline_code_html_escaped(self):
        """Ohne Escaping: `a < b` → <code>a < b</code> → `<b>` wird als HTML-Tag geparst."""
        import inspect
        from gui.panels.ai_panel import AIAssistantPanel
        source = inspect.getsource(AIAssistantPanel._format_code_blocks)
        self.assertNotIn(r'r\'<code style="background-color: #1e1e1e; padding: 2px 4px;">\1</code>\'', source,
                         "_format_code_blocks darf Inline-Code nicht ohne HTML-Escaping einsetzen")
        self.assertIn('escape_html', source,
                      "_format_code_blocks muss _escape_html für Inline-Code verwenden")


class TestNewProjectDialogAPIContract(unittest.TestCase):
    """Statischer Test: main_window ruft get_values(), nicht get_project_info()."""

    def test_main_window_calls_get_values_not_get_project_info(self):
        """main_window.py:_new_project rief get_project_info() — Methode existiert nicht → AttributeError."""
        main_source = (Path(__file__).parent.parent / 'src' / 'gui' / 'main_window.py').read_text(encoding='utf-8')
        self.assertNotIn('get_project_info', main_source,
                         "main_window.py darf get_project_info() nicht aufrufen — Methode heißt get_values()")
        from gui.dialogs.new_project_dialog import NewProjectDialog
        self.assertTrue(hasattr(NewProjectDialog, 'get_values'),
                        "NewProjectDialog muss get_values() definieren")


class TestBuildDialogWorkerCleanup(unittest.TestCase):
    """Statischer Test: BuildDialog muss reject() überschreiben um Worker zu stoppen."""

    def test_reject_overrides_to_stop_worker(self):
        """Ohne reject()-Override: Worker läuft nach Dialog-Schließen weiter → Crash."""
        import inspect
        from gui.dialogs.build_dialog import BuildDialog
        source = inspect.getsource(BuildDialog)
        self.assertIn('def reject(self)', source, "BuildDialog muss reject() überschreiben")
        self.assertIn('_worker.terminate()', source, "reject() muss terminate() aufrufen (quit() hat keinen Effekt ohne Event-Loop)")


class TestMainWindowShortcuts(unittest.TestCase):
    """Statischer Test: keine doppelten Keyboard-Shortcuts in main_window.py"""

    def test_no_duplicate_shortcuts(self):
        """Zwei Aktionen mit demselben Shortcut im selben Fenster führen zu Qt-Ambiguität."""
        import re
        source_path = Path(__file__).parent.parent / 'src' / 'gui' / 'main_window.py'
        source = source_path.read_text(encoding='utf-8')
        shortcuts = re.findall(r'setShortcut\(QKeySequence\("(.+?)"\)\)', source)
        non_empty = [s for s in shortcuts if s]
        duplicates = [s for s in set(non_empty) if non_empty.count(s) > 1]
        self.assertEqual(duplicates, [], f"Doppelte Shortcuts: {duplicates}")


class TestSettingsManagerGeneralSection(unittest.TestCase):
    """Bug 24: reset_to_defaults() setzte general.open_last_project nicht zurück."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_general_open_last_project_persists_round_trip(self):
        """general.open_last_project muss save/load-Round-Trip überstehen."""
        from core.settings_manager import SettingsManager
        path = os.path.join(self.temp_dir, 'settings.json')
        sm = SettingsManager(settings_path=path)
        sm.set('general.open_last_project', True)

        sm2 = SettingsManager(settings_path=path)
        self.assertTrue(sm2.get('general.open_last_project', False),
                        "general.open_last_project muss nach Reload True sein")

    def test_reset_to_defaults_clears_open_last_project(self):
        """reset_to_defaults() muss general.open_last_project auf False zurücksetzen."""
        from core.settings_manager import SettingsManager
        path = os.path.join(self.temp_dir, 'settings.json')
        sm = SettingsManager(settings_path=path)
        sm.set('general.open_last_project', True, save=False)
        sm.reset_to_defaults()
        self.assertFalse(sm.get('general.open_last_project', False),
                         "Nach reset_to_defaults muss open_last_project False sein")


class TestSettingsDialogGeneralTab(unittest.TestCase):
    """Bug 23: general.open_last_project war nicht über UI setzbar."""

    def test_settings_dialog_saves_open_last_project(self):
        """settings_dialog.py muss general.open_last_project speichern."""
        source = (Path(__file__).parent.parent / 'src' / 'gui' / 'dialogs' / 'settings_dialog.py').read_text(encoding='utf-8')
        self.assertIn("general.open_last_project", source,
                      "SettingsDialog muss general.open_last_project setzen")

    def test_settings_dialog_has_open_last_project_attribute(self):
        """SettingsDialog muss open_last_project-Widget besitzen."""
        import inspect
        from gui.dialogs.settings_dialog import SettingsDialog
        self.assertIn('open_last_project', inspect.getsource(SettingsDialog))


class TestSettingsDialogLineNumbersKey(unittest.TestCase):
    """Bug 27: settings_dialog verwendete 'editor.line_numbers' statt kanonischem 'editor.show_line_numbers'."""

    def test_dialog_uses_canonical_show_line_numbers_key(self):
        """editor.show_line_numbers ist das kanonische Feld; 'editor.line_numbers' landet in extra_settings."""
        import inspect
        from gui.dialogs.settings_dialog import SettingsDialog
        src = inspect.getsource(SettingsDialog._load_settings) + inspect.getsource(SettingsDialog._save_settings)
        self.assertIn('editor.show_line_numbers', src,
                      "Dialog muss 'editor.show_line_numbers' (kanonisch) verwenden")
        self.assertNotIn("'editor.line_numbers'", src,
                         "Dialog darf falschen Key 'editor.line_numbers' nicht mehr verwenden")

    def test_main_window_uses_canonical_key_directly(self):
        """_apply_editor_settings muss 'editor.show_line_numbers' direkt lesen, kein Fallback-Shim."""
        import inspect
        from gui.main_window import MainWindow
        src = inspect.getsource(MainWindow._apply_editor_settings)
        self.assertNotIn("'editor.line_numbers'", src,
                         "_apply_editor_settings darf 'editor.line_numbers' nicht mehr als Fallback lesen")
        self.assertIn('editor.show_line_numbers', src,
                      "_apply_editor_settings muss kanonischen Key 'editor.show_line_numbers' verwenden")


class TestCloseTabSavesCorrectEditor(unittest.TestCase):
    """Bug 26: _close_tab() rief _save_file() auf, das den aktiven (falschen) Tab speichert."""

    def test_close_tab_does_not_call_save_file_method(self):
        """_close_tab muss widget.save_file() direkt aufrufen, nicht self._save_file()."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._close_tab)
        self.assertNotIn('self._save_file()', source,
                         "_close_tab darf nicht self._save_file() aufrufen — spart aktiven Tab, nicht den zu schließenden")
        self.assertIn('widget.save_file', source,
                      "_close_tab muss widget.save_file() direkt aufrufen")


class TestMainWindowCloseEventNewFiles(unittest.TestCase):
    """Bug 25: closeEvent prüfte nur open_files, neue Dateien ohne Pfad wurden ignoriert."""

    def test_close_event_iterates_editor_tabs_not_open_files(self):
        """closeEvent muss editor_tabs iterieren, nicht open_files, damit neue Dateien erkannt werden."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow.closeEvent)
        self.assertIn('editor_tabs', source,
                      "closeEvent muss editor_tabs durchlaufen (nicht nur open_files)")
        self.assertNotIn('self.open_files.items()', source,
                         "closeEvent darf nicht mehr über self.open_files.items() iterieren")


class TestAIPanelNonCodeTextEscaped(unittest.TestCase):
    """Bug 35: _format_code_blocks() escapte nur Code-Blöcke, nicht den normalen Text.
    Vergleichsoperatoren wie x > 0 außerhalb von Code-Blöcken wurden als rohes HTML interpretiert."""

    def _make_panel(self):
        import sys
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            QApplication(sys.argv)
        from gui.panels.ai_panel import AIAssistantPanel
        return AIAssistantPanel()

    def test_non_code_text_with_angle_brackets_is_escaped(self):
        panel = self._make_panel()
        result = panel._format_code_blocks("Use x > 0 and x < 100")
        self.assertIn('&gt;', result, "'>'-Zeichen im normalen Text muss HTML-escaped werden")
        self.assertIn('&lt;', result, "'<'-Zeichen im normalen Text muss HTML-escaped werden")
        self.assertNotIn('<100', result, "Unescaped '<100' darf nicht im Output erscheinen")

    def test_code_block_still_formatted(self):
        panel = self._make_panel()
        result = panel._format_code_blocks("```python\nif x > 0:\n    pass\n```")
        self.assertIn('<pre', result, "Code-Blöcke müssen als <pre> formatiert werden")
        self.assertIn('&gt;', result, "'>'-Zeichen im Code-Block muss escaped werden")


class TestCloseEventNoSaveFileAsCall(unittest.TestCase):
    """Bug 34: closeEvent() rief _save_file_as() für unbenannte Dateien auf.
    _save_file_as() holt den Editor via _get_current_editor() (aktiver Tab), nicht den Editor aus der Schleife."""

    def test_close_event_does_not_delegate_to_save_file_as(self):
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow.closeEvent)
        self.assertNotIn('self._save_file_as()', source,
                         "closeEvent() darf _save_file_as() nicht aufrufen (würde falschen Editor speichern)")
        self.assertIn('QFileDialog', source,
                      "closeEvent() muss Save-As-Dialog direkt aufrufen")


class TestSaveFileAsRemovesOldPath(unittest.TestCase):
    """Bug 33: _save_file_as() entfernte den alten Pfad nicht aus open_files.
    Nach 'Speichern unter' zeigten beide Pfade auf denselben Editor."""

    def test_save_file_as_clears_old_open_files_entry(self):
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._save_file_as)
        self.assertIn('old_path', source,
                      "_save_file_as() muss den alten Pfad vor dem Speichern sichern")
        self.assertIn('del self.open_files', source,
                      "_save_file_as() muss den alten Eintrag aus open_files entfernen")

    def test_save_file_as_checks_save_return_value(self):
        """Regression: _save_file_as() muss den Rückgabewert von save_file() prüfen.
        Bei Fehler: open_files konsistent halten und Fehler-Dialog zeigen.
        Ohne Fix: open_files[new_path] gesetzt, old_path entfernt, obwohl Datei nicht gespeichert."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._save_file_as)
        self.assertIn('editor.save_file(path)', source,
                      "_save_file_as() muss den Rückgabewert von save_file(path) prüfen")
        # Der Rückgabewert muss ausgewertet werden — entweder via if oder Zuweisung
        self.assertTrue(
            'if editor.save_file(path)' in source or 'ok = editor.save_file(path)' in source,
            "_save_file_as() muss open_files nur bei erfolgreichem Speichern aktualisieren"
        )

    def test_save_file_checks_save_return_value(self):
        """Regression: _save_file() muss den Rückgabewert von save_file() prüfen.
        Bei Fehler soll ein Fehler-Dialog erscheinen, kein stilles Scheitern."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._save_file)
        self.assertIn('editor.save_file()', source,
                      "_save_file() muss save_file() aufrufen")
        self.assertNotIn('editor.save_file()\n', source,
                         "_save_file() darf den Rückgabewert nicht verwerfen (Zeile ohne Zuweisung/if)")


class TestNewProjectDialogOptionsUsed(unittest.TestCase):
    """Bug 32: _new_project() rief get_options() auf, nutzte das Ergebnis aber nie.
    Git-Init- und venv-Checkbox-Wahl des Users wurden still ignoriert."""

    def test_new_project_uses_init_git_option(self):
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._new_project)
        self.assertIn('init_git', source,
                      "_new_project() muss die init_git-Option aus get_options() verwenden")
        self.assertIn('git', source,
                      "_new_project() muss git init ausführen wenn init_git=True")


class TestAIServiceTemperaturePassthrough(unittest.TestCase):
    """Bug 31: complete() übergab temperature nie an die API — Einstellung hatte keinen Effekt."""

    def test_complete_includes_temperature_in_kwargs(self):
        import inspect
        from modules.ai_assistant.ai_service import AIService
        source = inspect.getsource(AIService.complete)
        self.assertIn('temperature', source,
                      "complete() muss temperature an den API-Aufruf übergeben")
        self.assertIn('self.temperature', source,
                      "complete() muss self.temperature in kwargs aufnehmen")


class TestLicenseGeneratorSubprocessEncoding(unittest.TestCase):
    """Bug 30: subprocess.run(..., text=True) ohne encoding='utf-8' → cp1252 auf Windows."""

    def test_get_licenses_subprocess_calls_use_utf8(self):
        import inspect
        from modules.builder.license_generator import LicenseGenerator
        source = inspect.getsource(LicenseGenerator.get_licenses)
        # Jeder text=True-Aufruf muss encoding='utf-8' daneben haben
        import re
        runs = re.findall(r'subprocess\.run\([^)]+\)', source, re.DOTALL)
        for call in runs:
            if 'text=True' in call:
                self.assertIn("encoding='utf-8'", call,
                              f"subprocess.run mit text=True benötigt encoding='utf-8': {call[:80]}")


class TestBuildDialogLoadDefaultsEncoding(unittest.TestCase):
    """Bug 29: _load_defaults() öffnete requirements.txt ohne encoding='utf-8'.
    UnicodeDecodeError wurde nicht abgefangen → Absturz bei UTF-8-Zeichen."""

    def test_load_defaults_uses_utf8_and_catches_unicode_error(self):
        import inspect
        from gui.dialogs.build_dialog import BuildDialog
        source = inspect.getsource(BuildDialog._load_defaults)
        self.assertIn("encoding='utf-8'", source,
                      "_load_defaults muss requirements.txt mit encoding='utf-8' öffnen")
        self.assertIn('UnicodeDecodeError', source,
                      "_load_defaults muss UnicodeDecodeError abfangen")


class TestSettingsManagerSavePreservesRecentProjects(unittest.TestCase):
    """Bug 28: SettingsManager._save() überschrieb recent_projects mit veralteter Kopie aus _extra_settings."""

    def test_save_preserves_recent_projects_written_by_project_manager(self):
        """_save() darf recent_projects nur aus der Datei lesen, nie mit der alten _extra_settings-Kopie überschreiben."""
        import inspect
        from core.settings_manager import SettingsManager
        source = inspect.getsource(SettingsManager._save)
        self.assertIn('recent_projects', source,
                      "_save() muss recent_projects aus der Datei lesen, bevor es schreibt")

    def test_save_reads_before_write_when_file_exists(self):
        """_save() liest aktuelle recent_projects aus der Datei und behält sie bei."""
        import tempfile, json, os, shutil
        from core.settings_manager import SettingsManager
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, 'settings.json')
            sm = SettingsManager(settings_path=path)
            # Simuliere: ProjectManager schreibt fresh recent_projects direkt in die Datei
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['recent_projects'] = ['/fresh/project']
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            # Jetzt SettingsManager speichern (z.B. User ändert Einstellung)
            sm.set('editor.font_size', 14)
            # recent_projects muss noch erhalten sein
            with open(path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            self.assertEqual(saved.get('recent_projects'), ['/fresh/project'],
                             "_save() darf frische recent_projects von ProjectManager nicht überschreiben")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestWinStorePublisherLambdaCapture(unittest.TestCase):
    """Bug 13: Lambda in except-Block fängt gelöschte Variable `e` ein.

    Python 3 löscht die Variable `e` aus `except Exception as e:` am Ende des
    except-Blocks. Ein Lambda, das `e` per Closure-Referenz nutzt, wirft dann
    NameError wenn es später (z.B. via Tkinter after()) ausgeführt wird.
    Fix: Wert vor dem Lambda in eine lokale Variable kopieren.
    """

    def _get_source(self):
        import pathlib
        p = (pathlib.Path(__file__).parent.parent
             / "resources" / "WinStorePackager" / "WindowsStorePublisher_3.py")
        return p.read_text(encoding="utf-8")

    def test_no_bare_lambda_e_in_except_blocks(self):
        """Kein Lambda darf die except-Variable `e` direkt (ohne Kopie) in einem f-String nutzen."""
        import re
        source = self._get_source()
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Suche nach self.after(0, lambda...) das {e} direkt enthält
            if ('self.after(' in stripped and 'lambda' in stripped and '{e}' in stripped):
                # Prüfe ob in den 4 vorangehenden Zeilen ein 'except ... as e:' steht
                context = '\n'.join(lines[max(0, i - 4):i])
                if re.search(r'except\s+\w[\w.]*\s+as\s+e\s*:', context):
                    self.fail(
                        f"Zeile {i + 1}: lambda nutzt {{e}} direkt in except-Block — "
                        f"NameError nach Block-Ende (Bug 13). Fix: err_msg = str(e) vor lambda."
                    )

    def test_err_msg_variable_used_in_build_thread(self):
        """build_thread() muss err_msg als Zwischenvariable vor dem Lambda setzen."""
        source = self._get_source()
        self.assertIn('err_msg = f"MSIX-Build fehlgeschlagen:', source,
                      "err_msg-Kopie vor Lambda in build_thread() fehlt (Bug 13 Fix)")


class TestProjectManagerUnknownFields(unittest.TestCase):
    """Bug 37 — ProjectConfig(**data) mit unbekannten Feldern"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from core.project_manager import ProjectManager
        self.pm = ProjectManager(settings_path=os.path.join(self.temp_dir, "settings.json"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_open_project_with_extra_fields(self):
        """open_project() darf bei unbekannten JSON-Feldern kein TypeError werfen."""
        import json
        from core.project_manager import ProjectManager
        proj_dir = os.path.join(self.temp_dir, "testproj")
        os.makedirs(proj_dir)
        data = {
            "name": "Test", "path": proj_dir,
            "created": "2025-01-01T00:00:00", "last_opened": "2025-01-01T00:00:00",
            "future_field": "some_value_from_newer_version"
        }
        with open(os.path.join(proj_dir, "devcenter.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        config = self.pm.open_project(proj_dir)
        self.assertIsNotNone(config, "open_project() muss auch bei unbekannten Feldern None vermeiden")
        self.assertEqual(config.name, "Test")


class TestKompilatorSubprocessEncoding(unittest.TestCase):
    """Bug 36 — Kompilator subprocess ohne encoding='utf-8'"""

    def test_check_pyinstaller_uses_utf8(self):
        """check_pyinstaller() muss encoding='utf-8' übergeben."""
        import inspect
        from modules.builder import Kompilator
        source = inspect.getsource(Kompilator.check_pyinstaller)
        self.assertIn("encoding='utf-8'", source,
                      "check_pyinstaller() muss encoding='utf-8' angeben")

    def test_popen_in_build_uses_utf8(self):
        """Popen-Aufruf in build() muss encoding='utf-8' verwenden."""
        import inspect
        from modules.builder import Kompilator
        source = inspect.getsource(Kompilator.build)
        self.assertIn("encoding='utf-8'", source,
                      "build() Popen muss encoding='utf-8' angeben")


class TestCloseEventChecksSaveReturnValue(unittest.TestCase):
    """closeEvent() muss den Rückgabewert von save_file() prüfen und bei Fehler abbrechen."""

    def test_close_event_checks_save_file_return_value(self):
        """Ohne Prüfung schließt das Fenster bei fehlgeschlagenem Speichern und Daten gehen verloren."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow.closeEvent)
        self.assertIn('not editor.save_file()', source,
                      "closeEvent muss save_file()-Rückgabewert prüfen")


class TestOutputPanelFailedToStartResetsUI(unittest.TestCase):
    """Statischer Test: OutputPanel._on_error muss bei FailedToStart die Buttons zurücksetzen."""

    def test_on_error_resets_buttons_on_failed_to_start(self):
        """Bei FailedToStart feuert Qt kein finished() — ohne Reset bleibt run_button dauerhaft deaktiviert."""
        import inspect
        from gui.panels.output_panel import OutputPanel
        source = inspect.getsource(OutputPanel._on_error)
        self.assertIn('FailedToStart', source,
                      "_on_error muss FailedToStart-Fall behandeln")
        self.assertIn('run_button.setEnabled(True)', source,
                      "_on_error muss run_button bei FailedToStart wieder aktivieren")


class TestNewProjectDialogPathUpdate(unittest.TestCase):
    """Statischer Test: path_edit muss textChanged mit _update_path verbinden."""

    def test_path_edit_connected_to_update_path(self):
        """Ohne Verbindung: manuelles Tippen in path_edit lässt full_path_label veralten."""
        import inspect
        from gui.dialogs.new_project_dialog import NewProjectDialog
        source = inspect.getsource(NewProjectDialog._setup_ui)
        self.assertIn('path_edit.textChanged.connect', source,
                      "path_edit.textChanged muss mit _update_path verbunden sein")


class TestCloseTabChecksSaveReturnValue(unittest.TestCase):
    """_close_tab() muss den Rückgabewert von save_file() prüfen und bei Fehler abbrechen."""

    def test_close_tab_checks_save_file_return_value(self):
        """Ohne Prüfung schließt der Tab bei fehlgeschlagenem Speichern und Daten gehen verloren."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._close_tab)
        self.assertIn('not widget.save_file()', source,
                      "_close_tab muss save_file()-Rückgabewert prüfen")


class TestCodeEditorLoadFileNoSpuriousSignal(unittest.TestCase):
    """CodeEditor.load_file() darf kein spurious file_modified(True) emittieren."""

    def test_load_file_suppresses_spurious_modified_signal(self):
        """setPlainText triggert textChanged; ohne Guard wird file_modified(True) fälschlich emittiert."""
        import inspect
        from modules.editor.code_editor import CodeEditor
        source = inspect.getsource(CodeEditor.load_file)
        # _is_modified=True muss VOR setPlainText erscheinen
        idx_guard = source.find('self._is_modified = True')
        idx_set = source.find('self.setPlainText(content)')
        self.assertGreater(idx_guard, -1, "load_file muss _is_modified=True vor setPlainText setzen")
        self.assertLess(idx_guard, idx_set,
                        "Guard _is_modified=True muss vor setPlainText(content) stehen")


class TestBuildDialogRejectUsesTerminate(unittest.TestCase):
    """Bug 10: reject() nutzte quit() auf synchronem QThread — hat keinen Effekt.
    Signale müssen vorher getrennt werden, dann terminate() statt quit()."""

    def test_reject_uses_terminate_not_quit(self):
        import inspect
        from gui.dialogs.build_dialog import BuildDialog
        source = inspect.getsource(BuildDialog.reject)
        self.assertNotIn('self._worker.quit()', source,
                         "reject() darf nicht quit() auf synchronem Worker aufrufen")
        self.assertIn('terminate()', source,
                      "reject() muss terminate() verwenden um synchronen Worker zu stoppen")

    def test_reject_disconnects_signals_before_terminating(self):
        import inspect
        from gui.dialogs.build_dialog import BuildDialog
        source = inspect.getsource(BuildDialog.reject)
        self.assertIn('disconnect', source,
                      "reject() muss Signale trennen bevor der Worker terminiert wird")


class TestOutputPanelRunCommandGuardCoversStartingState(unittest.TestCase):
    """Bug 9: run_command()-Guard prüfte nur == Running, nicht Starting.
    Programmatische Doppelaufrufe konnten gleichzeitig zwei Prozesse starten."""

    def test_run_command_guard_uses_not_equal_not_running(self):
        """Die Guard muss != NotRunning prüfen, damit auch der Starting-State abgedeckt ist."""
        import inspect
        from gui.panels.output_panel import OutputPanel
        source = inspect.getsource(OutputPanel.run_command)
        self.assertIn('NotRunning', source,
                      "run_command() muss QProcess.ProcessState.NotRunning referenzieren")
        self.assertNotIn('== QProcess.ProcessState.Running', source,
                         "run_command() darf nicht auf == Running prüfen (Starting-State nicht abgedeckt)")
        self.assertIn('!= QProcess.ProcessState.NotRunning', source,
                      "run_command() muss != NotRunning prüfen")


class TestWinStorePublisherSubprocessEncoding(unittest.TestCase):
    """Bug 12: subprocess.run mit text=True ohne encoding='utf-8' in WindowsStorePublisher_3.py.
    makeappx/signtool-Ausgaben können UnicodeDecodeError auf cp1252-Windows auslösen."""

    def _get_source(self):
        import pathlib
        p = pathlib.Path(__file__).parent.parent / "resources" / "WinStorePackager" / "WindowsStorePublisher_3.py"
        return p.read_text(encoding="utf-8")

    def test_text_true_always_paired_with_encoding_utf8(self):
        """Jeder subprocess-Aufruf mit text=True muss encoding='utf-8' enthalten."""
        import re
        source = self._get_source()
        calls = re.findall(r'subprocess\.(run|check_call|check_output|Popen)\([^)]+\)', source, re.DOTALL)
        for call in calls:
            if 'text=True' in call:
                self.assertIn("encoding='utf-8'", call,
                              f"subprocess-Aufruf mit text=True ohne encoding='utf-8': {call[:100]}")


class TestWinStorePublisherImageResamplingAPI(unittest.TestCase):
    """Bug 11: WindowsStorePublisher_3.py nutzte Image.LANCZOS (in Pillow 10.0 entfernt).
    Korrekte API: Image.Resampling.LANCZOS."""

    def _get_source(self):
        import pathlib
        p = pathlib.Path(__file__).parent.parent / "resources" / "WinStorePackager" / "WindowsStorePublisher_3.py"
        return p.read_text(encoding="utf-8")

    def test_old_lanczos_api_not_used(self):
        """Image.LANCZOS darf nicht mehr direkt aufgerufen werden (AttributeError auf Pillow 10+)."""
        import re
        source = self._get_source()
        # Erlaubt: Image.Resampling.LANCZOS — verboten: Image.LANCZOS ohne 'Resampling.'
        matches = re.findall(r'Image\.LANCZOS(?![\w.])', source)
        self.assertEqual(matches, [],
                         f"Image.LANCZOS (alte API) noch {len(matches)}× vorhanden — muss Image.Resampling.LANCZOS sein")

    def test_new_lanczos_api_used(self):
        """Image.Resampling.LANCZOS muss für alle resize()-Aufrufe genutzt werden."""
        source = self._get_source()
        self.assertIn('Image.Resampling.LANCZOS', source,
                      "WindowsStorePublisher_3.py muss Image.Resampling.LANCZOS verwenden")


class TestApplySettingsUpdatesModel(unittest.TestCase):
    """Bug B-001: _apply_settings() muss set_model() aufrufen."""

    def test_apply_settings_calls_set_model(self):
        """_apply_settings() muss ai.model lesen und set_model() aufrufen — ohne Fix wird
        die Modell-Auswahl in den Einstellungen vollständig ignoriert."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._apply_settings)
        self.assertIn('set_model', source,
                      "_apply_settings() muss set_model() aufrufen")
        self.assertIn('ai.model', source,
                      "_apply_settings() muss ai.model aus den Einstellungen lesen")

    def test_apply_settings_updates_max_tokens(self):
        """_apply_settings() muss auch ai.max_tokens auf den Service übertragen."""
        import inspect
        from gui.main_window import MainWindow
        source = inspect.getsource(MainWindow._apply_settings)
        self.assertIn('max_tokens', source,
                      "_apply_settings() muss ai.max_tokens auf ai_service übertragen")


class TestNewProjectDialogBorderReset(unittest.TestCase):
    """Bug B-002: Roter Validierungsrahmen muss bei textChanged zurückgesetzt werden."""

    def test_name_edit_textchanged_resets_style(self):
        """name_edit.textChanged muss mit _reset_name_style verbunden sein — ohne Fix
        bleibt der rote Rahmen auch nach Korrektur des Namens sichtbar."""
        import inspect
        from gui.dialogs.new_project_dialog import NewProjectDialog
        source = inspect.getsource(NewProjectDialog._setup_ui)
        self.assertIn('_reset_name_style', source,
                      "name_edit.textChanged muss mit _reset_name_style verbunden sein")

    def test_reset_name_style_clears_stylesheet(self):
        """_reset_name_style() muss das Stylesheet löschen (leerer String)."""
        import inspect
        from gui.dialogs.new_project_dialog import NewProjectDialog
        source = inspect.getsource(NewProjectDialog._reset_name_style)
        self.assertIn('setStyleSheet("")', source,
                      "_reset_name_style() muss setStyleSheet('') aufrufen")


if __name__ == "__main__":
    # Verbose Output
    unittest.main(verbosity=2)
