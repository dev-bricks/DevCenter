# -*- coding: utf-8 -*-
"""Regressionstests für ProfilerBridge — insbesondere Re-Index ohne FTS-Duplikate."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.filemanager.profiler_bridge import ProfilerBridge


class ProfilerBridgeTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        db_path = str(Path(self.tmp.name) / "test_index.db")
        self.bridge = ProfilerBridge(db_path=db_path)

    def _make_file(self, name: str, content: str = "hello") -> str:
        path = Path(self.tmp.name) / name
        path.write_text(content, encoding="utf-8")
        return str(path)

    def test_index_file_creates_entry(self):
        f = self._make_file("sample.py", "def foo(): pass")
        self.assertTrue(self.bridge.index_file(f))
        results = self.bridge.search("foo")
        self.assertEqual(len(results), 1)

    def test_reindex_same_file_no_duplicate_results(self):
        """Re-Indexieren einer Datei darf keine doppelten Such-Ergebnisse erzeugen.

        Bug: INSERT OR REPLACE auf AUTOINCREMENT-Tabelle ändert die id und hinterlässt
        einen verwaisten FTS-Eintrag. Nach N Re-Indizes liefert die Suche N Treffer
        für dieselbe Datei. Fix: ON CONFLICT DO UPDATE bewahrt die ursprüngliche id.
        """
        f = self._make_file("unique_module.py", "def alpha(): pass")

        for _ in range(5):
            self.bridge.index_file(f)

        results = self.bridge.search("alpha")
        paths = [r.file.path for r in results]
        self.assertEqual(
            len(paths),
            len(set(paths)),
            "Suche liefert Duplikate nach mehrfachem Re-Index derselben Datei",
        )
        self.assertEqual(len(results), 1, "Erwartet genau 1 Treffer, nicht mehr")

    def test_statistics_total_files_not_inflated(self):
        f = self._make_file("stats_test.py", "x = 1")
        for _ in range(3):
            self.bridge.index_file(f)
        stats = self.bridge.get_statistics()
        self.assertEqual(stats["total_files"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
