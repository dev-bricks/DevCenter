"""
Bugsweep Run #12 — Regressionstests (2026-06-20)

Bug #12-1: ai_panel.py — Stale-Response-Race beim Neustart des Workers.
           Jeder AIWorker besitzt ein eigenes response_received-Signal (separate QObjects,
           keine gemeinsame Connection). Das eigentliche Problem: Worker1 hat isRunning()=False
           zurückgegeben, aber sein emittiertes Signal liegt noch in der Qt-Event-Queue.
           Wird danach ein neuer Worker2 gestartet, kann _on_response Worker1's verspätete
           Antwort als Worker2-Antwort behandeln — falsche Chat-Nachricht, falscher Loading-State.
           Fix Teil 1: disconnect() vor dem Ersetzen des Workers (RuntimeError abfangen) —
           defensive Maßnahme, verkürzt das Race-Fenster aber eliminiert es nicht vollständig.
           Fix Teil 2 (der robuste Teil): Identitäts-Guard in _on_response
           (self.sender() is not self._worker → return) — verwirft Events veralteter Worker
           die noch in der Qt-Event-Queue lagen; dieser Guard schließt die Race vollständig.
"""
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAIPanelZombieSignal(unittest.TestCase):
    """Bug #12-1: AIAssistantPanel – fehlender disconnect() vor Worker-Neustart."""

    def test_start_request_disconnects_old_worker_before_new_connect(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        disconnect_pos = source.find("response_received.disconnect")
        connect_pos = source.find("response_received.connect")

        self.assertGreater(
            disconnect_pos, -1,
            "_start_request() muss response_received.disconnect() aufrufen",
        )
        self.assertGreater(
            connect_pos, -1,
            "_start_request() muss response_received.connect() aufrufen",
        )
        self.assertLess(
            disconnect_pos, connect_pos,
            "disconnect() muss VOR connect() im Quelltext stehen (verhindert doppelte Callbacks)",
        )

    def test_start_request_wraps_disconnect_in_try_except(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        pattern = r'try\s*:\s*\n\s*self\._worker\.response_received\.disconnect'
        self.assertIsNotNone(
            re.search(pattern, source),
            "disconnect() muss in try/except RuntimeError eingebettet sein",
        )


class TestAIPanelIdentityGuard(unittest.TestCase):
    """Bug #12-1 Teil 2: _on_response verwirft Events veralteter Worker per sender()-Guard."""

    def test_on_response_has_sender_identity_guard(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        self.assertIn(
            "self.sender() is not self._worker",
            source,
            "_on_response() muss einen sender()-Identitätsguard haben, der Events "
            "veralteter Worker (noch in der Qt-Event-Queue) verwirft",
        )

    def test_identity_guard_placed_before_set_loading(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        guard_pos = source.find("self.sender() is not self._worker")
        loading_pos = source.find("self._set_loading(False)")

        self.assertGreater(guard_pos, -1, "Sender-Guard muss in ai_panel.py vorhanden sein")
        self.assertGreater(loading_pos, -1, "_set_loading(False) muss in ai_panel.py vorhanden sein")
        self.assertLess(
            guard_pos, loading_pos,
            "sender()-Guard muss VOR _set_loading(False) stehen (Early-return vor Zustandsänderung)",
        )


class TestProjectManagerMetadataIntegrity(unittest.TestCase):
    """
    Bug B-004: ProjectManager Robustheit & Metadaten-Integrität
    - Absturz bei unvollständigen/minimalen Pflichtfeldern (path, created, last_opened)
    - Datenverlust benutzerdefinierter Felder in devcenter.json bei open_project & save_project
    - Geister-Einträge mit leerem Pfad in get_recent_projects
    - Überschreiben bestehender Codedateien beim Erstellen von Projekten
    """

    def setUp(self):
        import tempfile
        import sys
        self.temp_dir = tempfile.mkdtemp()
        sys_path_src = os.path.join(PROJECT_ROOT, "src")
        if sys_path_src not in sys.path:
            sys.path.insert(0, sys_path_src)
        from core.project_manager import ProjectManager
        self.settings_file = os.path.join(self.temp_dir, "settings.json")
        self.pm = ProjectManager(settings_path=self.settings_file)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_open_project_minimal_metadata(self):
        """open_project muss auch bei minimalem devcenter.json ohne path/created/last_opened gelingen."""
        import json
        proj_dir = os.path.join(self.temp_dir, "minimal_proj")
        os.makedirs(proj_dir, exist_ok=True)
        with open(os.path.join(proj_dir, "devcenter.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "MinimalProject"}, f)

        config = self.pm.open_project(proj_dir)
        self.assertIsNotNone(config, "open_project() darf bei fehlenden Pflichtfeldern nicht mit TypeError abstürzen")
        self.assertEqual(config.name, "MinimalProject")
        self.assertEqual(config.path, proj_dir)
        self.assertTrue(bool(config.created), "created muss automatisch initialisiert werden")
        self.assertTrue(bool(config.last_opened), "last_opened muss initialisiert werden")

    def test_open_project_preserves_custom_fields_on_disk(self):
        """open_project darf beim Speichern von last_opened keine benutzerdefinierten JSON-Felder löschen."""
        import json
        proj_dir = os.path.join(self.temp_dir, "custom_proj")
        os.makedirs(proj_dir, exist_ok=True)
        devcenter_path = os.path.join(proj_dir, "devcenter.json")
        initial_data = {
            "name": "CustomProj",
            "path": proj_dir,
            "created": "2026-01-01T00:00:00",
            "last_opened": "2026-01-01T00:00:00",
            "custom_plugin": "linter_x",
            "env_vars": {"DEBUG": "1"},
        }
        with open(devcenter_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        config = self.pm.open_project(proj_dir)
        self.assertIsNotNone(config)

        with open(devcenter_path, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertIn("custom_plugin", saved_data, "Custom-Felder müssen auf der Platte erhalten bleiben")
        self.assertEqual(saved_data["custom_plugin"], "linter_x")
        self.assertIn("env_vars", saved_data)
        self.assertEqual(saved_data["env_vars"], {"DEBUG": "1"})

    def test_save_project_preserves_custom_fields_on_disk(self):
        """save_project darf ebenfalls keine benutzerdefinierten JSON-Felder löschen."""
        import json
        proj_dir = os.path.join(self.temp_dir, "custom_proj_save")
        os.makedirs(proj_dir, exist_ok=True)
        devcenter_path = os.path.join(proj_dir, "devcenter.json")
        initial_data = {
            "name": "SaveProj",
            "path": proj_dir,
            "created": "2026-01-01T00:00:00",
            "last_opened": "2026-01-01T00:00:00",
            "custom_metadata": {"version": 42},
        }
        with open(devcenter_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        self.pm.open_project(proj_dir)
        self.pm.current_project.description = "Aktualisierte Beschreibung"
        self.assertTrue(self.pm.save_project())

        with open(devcenter_path, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data.get("description"), "Aktualisierte Beschreibung")
        self.assertIn("custom_metadata", saved_data, "Custom-Felder müssen durch save_project erhalten bleiben")
        self.assertEqual(saved_data["custom_metadata"], {"version": 42})

    def test_get_recent_projects_prunes_empty_and_whitespace_paths(self):
        """get_recent_projects muss Geister-Einträge mit leerem/Whitespace-Pfad entfernen."""
        import json
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump({
                "recent_projects": [
                    {"name": "EmptyPath", "path": ""},
                    {"name": "WhitespacePath", "path": "   "},
                    {"name": "ValidDir", "path": self.temp_dir},
                ]
            }, f)
        from core.project_manager import ProjectManager
        pm = ProjectManager(settings_path=self.settings_file)
        valid = pm.get_recent_projects()
        paths = [p.get("path") for p in valid]
        self.assertNotIn("", paths, "Leere Pfade dürfen nicht als existierend gewertet werden")
        self.assertNotIn("   ", paths, "Whitespace-Pfade dürfen nicht als existierend gewertet werden")
        self.assertEqual(len(valid), 1)

    def test_create_project_does_not_overwrite_existing_files(self):
        """create_project darf vorhandenen Quellcode nicht mit Vorlagentext überschreiben."""
        proj_dir = os.path.join(self.temp_dir, "existing_code_project")
        src_dir = os.path.join(proj_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        main_file = os.path.join(src_dir, "main.py")
        with open(main_file, "w", encoding="utf-8") as f:
            f.write("# Benutzerdefinierter Code\ndef custom(): pass\n")

        self.pm.create_project("ExistingCodeTest", proj_dir)

        with open(main_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# Benutzerdefinierter Code", content, "Bestehende main.py darf nicht überschrieben werden")
        self.assertNotIn("Hello from", content)


class TestMethodAnalyzerParameterAndNameCollection(unittest.TestCase):
    """
    Bug B-009: MethodAnalyzer AST Name Collection & Parameter Extraction
    - NameCollector übersieht posonlyargs, vararg (*args), kwonlyargs und kwarg (**kwargs)
    - NameCollector übersieht Lambda-Parameter, Exception-Handler-Aliase (except ... as e) und Match-Case-Pattern-Bindings
    - Führt zu False Positives bei undefined_names
    - _analyze_function unterschlägt posonlyargs, *vararg, kwonlyargs und **kwargs in MethodInfo.args
    """

    def setUp(self):
        import tempfile
        import sys
        self.temp_dir = tempfile.mkdtemp()
        sys_path_src = os.path.join(PROJECT_ROOT, "src")
        if sys_path_src not in sys.path:
            sys.path.insert(0, sys_path_src)
        from modules.analyzer.method_analyzer import MethodAnalyzer
        self.analyzer = MethodAnalyzer()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_varargs_and_kwargs_not_flagged_as_undefined_names(self):
        """Funktionen mit *args, **kwargs und kwonlyargs dürfen diese nicht als undefined_names melden."""
        code = '''
def process_data(a: int, *args: str, timeout: int = 30, **kwargs: float):
    if timeout > 0:
        return a, args, kwargs
'''
        file_path = os.path.join(self.temp_dir, "test_params.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        self.assertNotIn("args", result.undefined_names, "*args darf nicht als undefinierter Name gemeldet werden")
        self.assertNotIn("kwargs", result.undefined_names, "**kwargs darf nicht als undefinierter Name gemeldet werden")
        self.assertNotIn("timeout", result.undefined_names, "kwonlyarg darf nicht als undefinierter Name gemeldet werden")
        self.assertEqual(len(result.undefined_names), 0)

    def test_posonly_and_all_argument_kinds_in_method_info_args(self):
        """_analyze_function muss alle Parameterarten inklusive Annotationen in MethodInfo.args abbilden."""
        code = '''
def full_sig(pos_only: int, /, standard: str, *var_args: int, kw_only: bool = True, **extra: str) -> None:
    pass
'''
        file_path = os.path.join(self.temp_dir, "test_sig.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        self.assertEqual(len(result.functions), 1)
        func = result.functions[0]
        self.assertEqual(
            func.args,
            ["pos_only: int", "/", "standard: str", "*var_args: int", "kw_only: bool", "**extra: str"]
        )

    def test_lambda_parameters_not_flagged_as_undefined_names(self):
        """Parameter von Lambda-Ausdrücken dürfen nicht als undefined_names gemeldet werden."""
        code = '''
transform = lambda x, y=1: x + y
'''
        file_path = os.path.join(self.temp_dir, "test_lambda.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        self.assertNotIn("x", result.undefined_names)
        self.assertNotIn("y", result.undefined_names)
        self.assertEqual(len(result.undefined_names), 0)

    def test_except_handler_alias_not_flagged_as_undefined_names(self):
        """Exception-Alias (except ... as e) darf nicht als undefined_names gemeldet werden."""
        code = '''
try:
    pass
except Exception as err:
    print(err)
'''
        file_path = os.path.join(self.temp_dir, "test_except.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        self.assertNotIn("err", result.undefined_names)
        self.assertEqual(len(result.undefined_names), 0)

    def test_match_case_pattern_bindings_not_flagged_as_undefined_names(self):
        """Match-Case Pattern-Bindings (as-Name, MatchStar, MatchMapping rest) dürfen nicht als undefined gemeldet werden."""
        code = '''
data = [1, 2, 3]
match data:
    case [head, *tail] as seq:
        print(head, tail, seq)
    case {"status": s, **rest}:
        print(s, rest)
'''
        file_path = os.path.join(self.temp_dir, "test_match.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        for expected in ["head", "tail", "seq", "s", "rest"]:
            self.assertNotIn(expected, result.undefined_names)
        self.assertEqual(len(result.undefined_names), 0)

    def test_builtin_exceptions_not_flagged_as_undefined_names(self):
        """Standard-Exceptions wie SyntaxError, PermissionError, TimeoutError dürfen nicht als undefined gelten."""
        code = '''
try:
    pass
except (SyntaxError, PermissionError, TimeoutError, UnicodeDecodeError):
    pass
'''
        file_path = os.path.join(self.temp_dir, "test_builtins.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.analyzer.analyze_file(file_path)
        self.assertEqual(len(result.undefined_names), 0)


if __name__ == "__main__":
    unittest.main()


