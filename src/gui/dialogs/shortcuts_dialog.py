# -*- coding: utf-8 -*-
"""
DevCenter - Shortcuts Dialog
Barrierefreier Hilfedialog für alle Tastaturkürzel nach WCAG 2.1 AA und BITV 2.0.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ShortcutsDialog(QDialog):
    """Barrierefreier Referenzdialog für alle Tastaturkürzel und Schnellzugriffe."""

    SHORTCUTS: List[Tuple[str, str, str]] = [
        # (Kategorie, Tastenkombination, Beschreibung)
        ("Datei & Projekt", "Ctrl+Shift+N", "Neues Projekt erstellen"),
        ("Datei & Projekt", "Ctrl+Shift+O", "Bestehendes Projekt öffnen"),
        ("Datei & Projekt", "Ctrl+N", "Neue Datei erstellen"),
        ("Datei & Projekt", "Ctrl+O", "Datei öffnen"),
        ("Datei & Projekt", "Ctrl+W", "Aktiven Reiter / Datei schließen"),
        ("Datei & Projekt", "Ctrl+S", "Aktuelle Datei speichern"),
        ("Datei & Projekt", "Ctrl+Shift+S", "Datei speichern unter"),
        ("Datei & Projekt", "Ctrl+,", "Einstellungen öffnen"),
        ("Datei & Projekt", "Ctrl+Q / Alt+F4", "DevCenter beenden"),
        ("Bearbeiten & Suchen", "Ctrl+Z", "Rückgängig"),
        ("Bearbeiten & Suchen", "Ctrl+Y", "Wiederholen"),
        ("Bearbeiten & Suchen", "Ctrl+X", "Ausschneiden"),
        ("Bearbeiten & Suchen", "Ctrl+C", "Kopieren"),
        ("Bearbeiten & Suchen", "Ctrl+V", "Einfügen"),
        ("Bearbeiten & Suchen", "Ctrl+F", "Suchdialog im Editor öffnen"),
        ("Bearbeiten & Suchen", "Ctrl+H", "Suchen und Ersetzen"),
        ("Bearbeiten & Suchen", "F3", "Nächsten Treffer suchen"),
        ("Bearbeiten & Suchen", "Shift+F3", "Vorherigen Treffer suchen"),
        ("Ansicht & Navigation", "Ctrl+Tab", "Nächster Editor-Reiter"),
        ("Ansicht & Navigation", "Ctrl+Shift+Tab", "Vorheriger Editor-Reiter"),
        ("Ansicht & Navigation", "Ctrl+1 .. Ctrl+9", "Direkt zu Editor-Reiter 1–9 springen"),
        ("Ansicht & Navigation", "Ctrl+Shift+A", "AI-Assistent ein-/ausblenden"),
        ("Ansicht & Navigation", "Ctrl+Alt+[", "Aktuellen Code-Block falten"),
        ("Ansicht & Navigation", "Ctrl+Alt+]", "Aktuellen Code-Block entfalten"),
        ("Ansicht & Navigation", "Ctrl+Alt+0", "Alle Code-Blöcke entfalten"),
        ("Ansicht & Navigation", "Alt+D", "Menü Datei öffnen"),
        ("Ansicht & Navigation", "Alt+B", "Menü Bearbeiten öffnen"),
        ("Ansicht & Navigation", "Alt+A", "Menü Ansicht öffnen"),
        ("Ansicht & Navigation", "Alt+U", "Menü Ausführen öffnen"),
        ("Ansicht & Navigation", "Alt+N", "Menü Analyse öffnen"),
        ("Ansicht & Navigation", "Alt+H", "Menü Hilfe öffnen"),
        ("Ausführen & Analyse", "F5", "Aktuelle Datei ausführen"),
        ("Ausführen & Analyse", "F6", "Build-Dialog öffnen"),
        ("Ausführen & Analyse", "Ctrl+F7", "Aktuelle Datei analysieren"),
        ("Hilfe & Barrierefreiheit", "F1", "Tastaturkürzel & Hilfe anzeigen"),
        ("Hilfe & Barrierefreiheit", "Shift+F1", "Über DevCenter (System & Lizenz)"),
        ("Hilfe & Barrierefreiheit", "Escape", "Dialoge und Popups schließen"),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tastaturkürzel & Hilfe")
        self.setObjectName("ShortcutsDialog")
        self.setAccessibleName("Tastaturkürzel und Bedienungshilfe")
        self.setAccessibleDescription(
            "Vollständige Referenz aller Tastenkombinationen in DevCenter nach WCAG 2.1 AA und BITV 2.0 Standards."
        )
        self.setModal(True)
        self.setMinimumSize(700, 540)
        self.resize(760, 580)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Styling dunkel an DevCenter angepasst
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QTableWidget {
                background-color: #252526;
                color: #e0e0e0;
                gridline-color: #333333;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                selection-background-color: #094771;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px 8px;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 8px;
                border: 1px solid #3c3c3c;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton:focus {
                outline: 2px solid #007acc;
            }
        """)

        # Titelzeile
        header_layout = QVBoxLayout()
        self.lbl_title = QLabel("⌨️ Tastaturkürzel & Schnelle Navigation")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        self.lbl_title.setAccessibleName("Titel Tastaturkürzel")
        header_layout.addWidget(self.lbl_title)

        self.lbl_a11y_notice = QLabel(
            "Barrierefreiheit (WCAG 2.1 AA / BITV 2.0): Sämtliche Kernfunktionen von DevCenter sind "
            "ohne Maus vollständig über die Tastatur bedienbar. Drücken Sie F1 für diese Übersicht oder Escape zum Schließen."
        )
        self.lbl_a11y_notice.setWordWrap(True)
        self.lbl_a11y_notice.setStyleSheet("color: #4ec9b0; font-size: 12px; line-height: 1.4;")
        self.lbl_a11y_notice.setAccessibleName("Hinweis zur Barrierefreiheit und Tastaturbedienung")
        header_layout.addWidget(self.lbl_a11y_notice)
        layout.addLayout(header_layout)

        # Tabelle
        self.table = QTableWidget(self)
        self.table.setObjectName("ShortcutsTable")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Kategorie", "Tastenkombination", "Aktion"])
        self.table.setAccessibleName("Tabelle der Tastaturkürzel")
        self.table.setAccessibleDescription("Liste aller verfügbaren Tastenkombinationen sortiert nach Kategorien")
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self._populate_table()
        layout.addWidget(self.table)

        # Fußzeile mit Schließen-Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_close = QPushButton("Schließen")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setAccessibleName("Dialog schließen")
        self.btn_close.setAccessibleDescription("Schließt die Tastaturkürzel-Übersicht")
        self.btn_close.setDefault(True)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # Tastaturfokus auf Schließen-Button setzen
        self.btn_close.setFocus()

    def _populate_table(self) -> None:
        """Befüllt die Tabelle mit allen Tastaturkombinationen."""
        self.table.setRowCount(len(self.SHORTCUTS))
        for row, (category, shortcut, action) in enumerate(self.SHORTCUTS):
            item_cat = QTableWidgetItem(category)
            item_sc = QTableWidgetItem(shortcut)
            item_act = QTableWidgetItem(action)

            item_cat.setFlags(item_cat.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_sc.setFlags(item_sc.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_act.setFlags(item_act.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Tastenkürzel leicht hervorheben
            item_sc.setForeground(Qt.GlobalColor.cyan)

            self.table.setItem(row, 0, item_cat)
            self.table.setItem(row, 1, item_sc)
            self.table.setItem(row, 2, item_act)

    def keyPressEvent(self, event) -> None:
        """Escape schließt den Dialog barrierefrei."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)
