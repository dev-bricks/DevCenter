# -*- coding: utf-8 -*-
"""
DevCenter - UX & Accessibility (A11y) Integration- und Vertragstests
Konformität: WCAG 2.1 AA und BITV 2.0

Verifiziert:
1. Menüleiste: Barrierefreier Name, Beschreibung und Alt-Mnemonics
2. Hilfe-Menü & Accelerators: F1 (Tastaturkürzel & Hilfe) und Shift+F1 (Über DevCenter)
3. Datei-Menü: Ctrl+W (Datei schließen) und Ctrl+Q / Alt+F4 (Beenden)
4. Ansicht-Menü: Ctrl+Tab (Nächster Reiter) und Ctrl+Shift+Tab (Vorheriger Reiter)
5. Hauptwerkzeugleiste: Barrierefreier Name, Tooltips mit Tastenkürzeln und sprechende Accessible Names
6. Reiter-Navigation: Editor-Tabs und Ausgabe-Tabs mit Accessible Names & Descriptions
7. Tab-Wechsel- und Schließlogik: _close_current_tab, _next_editor_tab, _prev_editor_tab, _switch_to_editor_tab
8. Statusleiste: Barrierefreier Name und Accessible Names für Status-Widgets
9. ShortcutsDialog: Barrierefreier Tastaturkürzel-Dialog mit Tabelle, Kategorien, BITV/WCAG-Hinweis und Escape-Dismiss
10. AboutDialog: Barrierefreier Über-Dialog mit Version 1.0.3, GPL-3.0, Local-First Invariante und Escape-Dismiss
11. Deutsche Typografie: Echte Umlaute (ä, ö, ü, Ä, Ö, Ü, ß) in allen End-User-Texten
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

# Pfade
APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(APP_ROOT / "src"))

from gui.main_window import MainWindow
from gui.dialogs.shortcuts_dialog import ShortcutsDialog
from gui.dialogs.about_dialog import AboutDialog


class TestDevCenterUIAccessibility(unittest.TestCase):
    """Prüft die Einhaltung der WCAG 2.1 AA / BITV 2.0 Standards in DevCenter."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()

    # --- 1. Menüleiste & Mnemonics ---

    def test_menubar_accessibility_and_mnemonics(self):
        """Prüft, ob die Menüleiste barrierefreie Attribute und Alt-Mnemonics besitzt."""
        menubar = self.window.menuBar()
        self.assertEqual(menubar.accessibleName(), "Hauptmenü")
        self.assertIn("Hauptmenüzeile", menubar.accessibleDescription())

        menu_titles = [action.text() for action in menubar.actions()]
        self.assertIn("&Datei", menu_titles)
        self.assertIn("&Bearbeiten", menu_titles)
        self.assertIn("&Ansicht", menu_titles)
        self.assertIn("&Ausführen", menu_titles)
        self.assertIn("&Analyse", menu_titles)
        self.assertIn("&Hilfe", menu_titles)

    # --- 2. Hilfe-Menü & Tastenkürzel F1 / Shift+F1 ---

    def test_help_menu_actions_and_shortcuts(self):
        """Prüft Tastaturkürzel F1 und Shift+F1 im Hilfe-Menü."""
        menubar = self.window.menuBar()
        help_action = [a for a in menubar.actions() if a.text() == "&Hilfe"][0]
        help_menu = help_action.menu()
        self.assertIsNotNone(help_menu)

        actions = help_menu.actions()
        shortcuts_act = [a for a in actions if "Tastaturkürzel" in a.text()][0]
        about_act = [a for a in actions if "Über DevCenter" in a.text()][0]

        self.assertEqual(shortcuts_act.shortcut().toString(), "F1")
        self.assertEqual(about_act.shortcut().toString(), "Shift+F1")

    # --- 3. Datei-Menü & Schließen / Beenden ---

    def test_file_menu_close_tab_and_exit_shortcuts(self):
        """Prüft Ctrl+W für Datei schließen und Ctrl+Q / Alt+F4 für Beenden."""
        menubar = self.window.menuBar()
        file_action = [a for a in menubar.actions() if a.text() == "&Datei"][0]
        file_menu = file_action.menu()
        self.assertIsNotNone(file_menu)

        actions = file_menu.actions()
        close_tab_act = [a for a in actions if a.text() == "Datei schließen"][0]
        exit_act = [a for a in actions if a.text() == "Beenden"][0]

        self.assertEqual(close_tab_act.shortcut().toString(), "Ctrl+W")
        shortcuts = [s.toString() for s in exit_act.shortcuts()]
        self.assertTrue("Ctrl+Q" in shortcuts or "Alt+F4" in shortcuts)

    # --- 4. Ansicht-Menü & Tab-Navigation ---

    def test_view_menu_tab_navigation_actions(self):
        """Prüft Ctrl+Tab und Ctrl+Shift+Tab im Ansicht-Menü."""
        menubar = self.window.menuBar()
        view_action = [a for a in menubar.actions() if a.text() == "&Ansicht"][0]
        view_menu = view_action.menu()
        self.assertIsNotNone(view_menu)

        actions = view_menu.actions()
        next_tab_act = [a for a in actions if a.text() == "Nächster Reiter"][0]
        prev_tab_act = [a for a in actions if a.text() == "Vorheriger Reiter"][0]

        self.assertEqual(next_tab_act.shortcut().toString(), "Ctrl+Tab")
        self.assertEqual(prev_tab_act.shortcut().toString(), "Ctrl+Shift+Tab")

    # --- 5. Hauptwerkzeugleiste ---

    def test_toolbar_accessibility_names_and_tooltips(self):
        """Prüft barrierefreie Namen und informative Tooltips auf der Hauptwerkzeugleiste."""
        toolbar = None
        for child in self.window.children():
            if child.__class__.__name__ == "QToolBar":
                toolbar = child
                break
        self.assertIsNotNone(toolbar)
        self.assertEqual(toolbar.accessibleName(), "Hauptwerkzeugleiste")
        self.assertIn("Schnellzugriff", toolbar.accessibleDescription())

        toolbar_actions = toolbar.actions()
        buttons = [toolbar.widgetForAction(a) for a in toolbar_actions if toolbar.widgetForAction(a)]
        action_names = [b.accessibleName() for b in buttons if b.accessibleName()]
        self.assertIn("Neues Projekt", action_names)
        self.assertIn("Projekt öffnen", action_names)
        self.assertIn("Datei speichern", action_names)
        self.assertIn("Ausführen", action_names)
        self.assertIn("Build erstellen", action_names)
        self.assertIn("Datei analysieren", action_names)
        self.assertIn("AI-Assistent", action_names)

        # Tooltips mit Tastaturhinweisen
        tooltips = [a.toolTip() for a in toolbar_actions if a.toolTip()]
        self.assertTrue(any("Ctrl+Shift+N" in tip for tip in tooltips))
        self.assertTrue(any("Ctrl+Shift+O" in tip for tip in tooltips))
        self.assertTrue(any("Ctrl+S" in tip for tip in tooltips))
        self.assertTrue(any("F5" in tip for tip in tooltips))
        self.assertTrue(any("F6" in tip for tip in tooltips))
        self.assertTrue(any("Ctrl+F7" in tip for tip in tooltips))
        self.assertTrue(any("Ctrl+Shift+A" in tip for tip in tooltips))

    # --- 6. Reiter-Barrierefreiheit ---

    def test_tabs_accessibility_attributes(self):
        """Prüft AccessibleName und AccessibleDescription für Editor- und Output-Tabs."""
        self.assertEqual(self.window.editor_tabs.accessibleName(), "Editor-Reiter")
        self.assertIn("Geöffnete Dokumente", self.window.editor_tabs.accessibleDescription())

        self.assertEqual(self.window.output_tabs.accessibleName(), "Ausgabe-Reiter")
        self.assertIn("Terminal-Ausgabe", self.window.output_tabs.accessibleDescription())

    # --- 7. Tab-Wechsel und Schließen ---

    def test_tab_switching_and_closing_logic(self):
        """Prüft zyklisches Wechseln und Schließen von Reitern."""
        initial_count = self.window.editor_tabs.count()
        self.assertGreaterEqual(initial_count, 1)

        # Neue Dateien öffnen
        self.window._new_file()
        self.window._new_file()
        self.assertEqual(self.window.editor_tabs.count(), initial_count + 2)

        # Direkt-Sprung zu Tab 0
        self.window._switch_to_editor_tab(0)
        self.assertEqual(self.window.editor_tabs.currentIndex(), 0)

        # Nächster Tab
        self.window._next_editor_tab()
        self.assertEqual(self.window.editor_tabs.currentIndex(), 1)

        # Vorheriger Tab
        self.window._prev_editor_tab()
        self.assertEqual(self.window.editor_tabs.currentIndex(), 0)

        # Aktiven Tab schließen via _close_current_tab
        self.window._close_current_tab()
        self.assertEqual(self.window.editor_tabs.count(), initial_count + 1)

    # --- 8. Statusleiste ---

    def test_statusbar_accessibility_labels(self):
        """Prüft AccessibleName und AccessibleDescription der Statusleiste und ihrer Widgets."""
        statusbar = self.window.statusBar()
        self.assertEqual(statusbar.accessibleName(), "Statusleiste")
        self.assertIn("Statusmeldungen", statusbar.accessibleDescription())

        self.assertEqual(self.window.project_label.accessibleName(), "Aktives Projekt")
        self.assertEqual(self.window.cursor_label.accessibleName(), "Cursorposition")
        self.assertEqual(self.window.encoding_label.accessibleName(), "Zeichenkodierung")

    # --- 9. ShortcutsDialog ---

    def test_shortcuts_dialog_lifecycle_and_a11y(self):
        """Prüft Struktur, Tabelle, Kategorien, WCAG/BITV Hinweis und Escape-Taste im ShortcutsDialog."""
        dialog = ShortcutsDialog(self.window)
        self.assertEqual(dialog.accessibleName(), "Tastaturkürzel und Bedienungshilfe")
        self.assertIn("WCAG 2.1 AA", dialog.accessibleDescription())
        self.assertIn("BITV 2.0", dialog.accessibleDescription())

        # Tabelle
        self.assertEqual(dialog.table.columnCount(), 3)
        self.assertGreaterEqual(dialog.table.rowCount(), 30)

        # Kategorien prüfen
        categories = {dialog.table.item(row, 0).text() for row in range(dialog.table.rowCount())}
        self.assertIn("Datei & Projekt", categories)
        self.assertIn("Bearbeiten & Suchen", categories)
        self.assertIn("Ansicht & Navigation", categories)
        self.assertIn("Ausführen & Analyse", categories)
        self.assertIn("Hilfe & Barrierefreiheit", categories)

        # Schließen-Button ist Default-Button
        self.assertTrue(dialog.btn_close.isDefault())

        # Escape-Taste schließt Dialog
        escape_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        dialog.keyPressEvent(escape_event)
        self.assertEqual(dialog.result(), ShortcutsDialog.DialogCode.Rejected)
        dialog.close()

    # --- 10. AboutDialog ---

    def test_about_dialog_lifecycle_and_a11y(self):
        """Prüft Über-Dialog mit Version, Lizenz, Local-First Invariante und Escape-Taste."""
        dialog = AboutDialog(self.window)
        self.assertEqual(dialog.accessibleName(), "Über DevCenter")
        self.assertIn("1.0.3", dialog.accessibleDescription())
        self.assertIn("GPL-3.0", dialog.accessibleDescription())
        self.assertIn("Local-First", dialog.accessibleDescription())

        # Titel & Version
        self.assertIn("DevCenter", dialog.title_label.text())
        self.assertIn("1.0.3", dialog.version_label.text())

        # Local-First / Zero-Egress Reassurance
        desc_text = dialog.accessibleDescription()
        self.assertIn("Local-First", desc_text)

        # Escape schließt Dialog
        escape_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        dialog.keyPressEvent(escape_event)
        self.assertEqual(dialog.result(), AboutDialog.DialogCode.Rejected)
        dialog.close()

    # --- 11. Deutsche Typografie & Echte Umlaute ---

    def test_german_typography_and_real_umlauts(self):
        """Stellt sicher, dass deutsche End-User-Texte echte Umlaute (ä, ö, ü, Ä, Ö, Ü, ß) nutzen."""
        dialog = ShortcutsDialog(self.window)
        for row in range(dialog.table.rowCount()):
            text = dialog.table.item(row, 2).text()
            self.assertNotIn("oeffnen", text)
            self.assertNotIn("schliessen", text)
            self.assertNotIn("zurueck", text)
            self.assertNotIn("fuer", text)

        about = AboutDialog(self.window)
        name = about.accessibleName()
        self.assertIn("Über", name)
        self.assertNotIn("ueber", name.lower())
        self.assertNotIn("fuer", about.accessibleDescription().lower())

        dialog.close()
        about.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
