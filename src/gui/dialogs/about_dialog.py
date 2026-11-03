# -*- coding: utf-8 -*-
"""
DevCenter - About Dialog
Barrierefreier Über-Dialog mit Versions-, Lizenz-, Datenschutz- und Accessibility-Angaben
gemäß WCAG 2.1 AA und BITV 2.0 Standards.
"""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AboutDialog(QDialog):
    """Barrierefreier Über-Dialog für DevCenter."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Über DevCenter")
        self.setObjectName("AboutDialog")
        self.setAccessibleName("Über DevCenter")
        self.setAccessibleDescription(
            "Informationen zur Anwendung DevCenter, Version 1.0.3, GPL-3.0 Lizenz, "
            "Local-First Architektur und Barrierefreiheit nach WCAG 2.1 AA und BITV 2.0."
        )
        self.setModal(True)
        self.setMinimumWidth(580)
        self.setMinimumHeight(480)
        self.resize(620, 520)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Dunkles Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QGroupBox {
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #4ec9b0;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 22px;
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

        # Kopfbereich mit App-Icon und Titel
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("about_icon_label")
        self.icon_label.setAccessibleName("DevCenter App-Symbol")
        icon = self.windowIcon()
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(56, 56))
        else:
            self.icon_label.setText("🚀")
            self.icon_label.setStyleSheet("font-size: 40px;")
        header_layout.addWidget(self.icon_label)

        title_layout = QVBoxLayout()
        self.title_label = QLabel("<h2>DevCenter</h2>")
        self.title_label.setObjectName("about_title_label")
        self.title_label.setStyleSheet("color: #ffffff; margin: 0; padding: 0;")
        self.title_label.setAccessibleName("Anwendungsname DevCenter")
        title_layout.addWidget(self.title_label)

        self.version_label = QLabel("<b>Version 1.0.3</b> — Python Development Suite")
        self.version_label.setObjectName("about_version_label")
        self.version_label.setStyleSheet("color: #4ec9b0; font-size: 13px;")
        self.version_label.setAccessibleName("Version 1.0.3 Python Development Suite")
        title_layout.addWidget(self.version_label)

        self.subtitle_label = QLabel("Integrierte Entwicklungsumgebung für den kompletten Python-Lebenszyklus.")
        self.subtitle_label.setObjectName("about_subtitle_label")
        self.subtitle_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        self.subtitle_label.setWordWrap(True)
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Gruppe 1: Architektur & Fusionierte Werkzeuge
        tools_group = QGroupBox("Architektur & Integrierte Werkzeuge")
        tools_group.setAccessibleName("Architektur und integrierte Werkzeuge")
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setSpacing(4)

        lbl_tools = QLabel(
            "• <b>PythonBox:</b> Vollwertiger Code-Editor mit Syntax-Highlighting und Code-Faltung<br>"
            "• <b>MethodenAnalyser:</b> Statische AST-Code-Analyse und Methoden-Prüfung<br>"
            "• <b>UltimateKompilator:</b> Standalone-Executable-Erstellung via PyInstaller<br>"
            "• <b>Entwicklerschleife:</b> Integrierte AI-Assistenz und automatisierte Code-Generierung<br>"
            "• <b>ProFiler / ProSync:</b> Schnelle Dateiverwaltung und Workspace-Export"
        )
        lbl_tools.setWordWrap(True)
        lbl_tools.setStyleSheet("line-height: 1.4; color: #dddddd;")
        tools_layout.addWidget(lbl_tools)
        layout.addWidget(tools_group)

        # Gruppe 2: Lizenz & Datenschutz
        license_group = QGroupBox("Lizenz & Datenschutz")
        license_group.setAccessibleName("Lizenz und Datenschutz")
        license_layout = QVBoxLayout(license_group)
        license_layout.setSpacing(4)

        lbl_license = QLabel(
            "• <b>Lizenz:</b> GNU General Public License v3.0 (GPL-3.0) — Freie und quelloffene Software.<br>"
            "• <b>Datenschutz & Privatsphäre:</b> 100% Local-First / Zero-Egress. Sämtliche Quelltexte, "
            "Projektanalysen und Builds verbleiben vollständig lokal auf Ihrem Rechner. "
            "Es werden keine Telemetriedaten oder Analysedaten an externe Server übertragen."
        )
        lbl_license.setWordWrap(True)
        lbl_license.setStyleSheet("line-height: 1.4; color: #dddddd;")
        license_layout.addWidget(lbl_license)
        layout.addWidget(license_group)

        # Gruppe 3: Barrierefreiheit & Konformität
        a11y_group = QGroupBox("Barrierefreiheit (Accessibility)")
        a11y_group.setAccessibleName("Barrierefreiheit und Konformität")
        a11y_layout = QVBoxLayout(a11y_group)
        a11y_layout.setSpacing(4)

        lbl_a11y = QLabel(
            "• <b>Konformitätsstandard:</b> Entwickelt nach den Richtlinien der <b>WCAG 2.1 AA</b> und <b>BITV 2.0</b>.<br>"
            "• <b>Tastaturbedienung:</b> Vollständige Tastatur-Navigation aller Menüs, Dialoge und Reiter. "
            "Drücken Sie <b>F1</b> für die Tastaturkürzel-Referenz oder <b>Ctrl+W</b> zum Schließen aktiver Reiter.<br>"
            "• <b>Screenreader:</b> Alle Oberflächenelemente sind mit barrierefreien Namen und Beschreibungen ausgestattet."
        )
        lbl_a11y.setWordWrap(True)
        lbl_a11y.setStyleSheet("line-height: 1.4; color: #dddddd;")
        a11y_layout.addWidget(lbl_a11y)
        layout.addWidget(a11y_group)

        layout.addStretch()

        # Schließen-Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_close = QPushButton("Schließen")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setAccessibleName("Dialog schließen")
        self.btn_close.setAccessibleDescription("Schließt das Fenster Über DevCenter")
        self.btn_close.setDefault(True)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # Fokus auf Schließen-Button
        self.btn_close.setFocus()

    def keyPressEvent(self, event) -> None:
        """Escape schließt den Dialog barrierefrei."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)
