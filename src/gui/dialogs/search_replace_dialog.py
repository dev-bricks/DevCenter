# -*- coding: utf-8 -*-
"""Nicht-modaler Dialog für die Editor-Suche und das Ersetzen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class SearchReplaceDialog(QDialog):
    """UI-Vertrag für Suche/Ersetzen ohne Änderung am Dokument beim Abbruch.

    Die eigentliche Dokumentoperation bleibt beim ``CodeEditor``.  Dadurch
    bleiben Cursor, Tab und UTF-8-Inhalt im aktiven Editor und der Dialog kann
    bei Tabwechseln wiederverwendet werden.
    """

    find_next_requested = Signal(str, bool, bool, bool, str)
    find_previous_requested = Signal(str, bool, bool, bool, str)
    replace_requested = Signal(str, str, bool, bool, bool, str)
    replace_all_requested = Signal(str, str, bool, bool, bool, str)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Suchen und Ersetzen")
        self.setModal(False)
        self.setMinimumWidth(460)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Suchbegriff")
        self.search_input.setAccessibleName("Suchbegriff")

        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Ersetzung (leer erlaubt)")
        self.replace_input.setAccessibleName("Ersetzung")

        self.case_sensitive = QCheckBox("Groß-/Kleinschreibung beachten", self)
        self.case_sensitive.setAccessibleName("Groß-/Kleinschreibung beachten")
        self.whole_word = QCheckBox("Nur ganze Wörter", self)
        self.whole_word.setAccessibleName("Nur ganze Wörter")
        self.regex = QCheckBox("Regulärer Ausdruck", self)
        self.regex.setAccessibleName("Regulärer Ausdruck")

        self.scope_combo = QComboBox(self)
        self.scope_combo.addItem("Gesamtes Dokument", "document")
        self.scope_combo.addItem("Aktuelle Auswahl", "selection")
        self.scope_combo.setAccessibleName("Suchbereich")

        self.status_label = QLabel("", self)
        self.status_label.setWordWrap(True)

        self.find_previous_button = QPushButton("Vorheriger Treffer", self)
        self.find_previous_button.setObjectName("findPreviousButton")
        self.find_next_button = QPushButton("Nächster Treffer", self)
        self.find_next_button.setObjectName("findNextButton")
        self.replace_button = QPushButton("Ersetzen", self)
        self.replace_button.setObjectName("replaceButton")
        self.replace_all_button = QPushButton("Alle ersetzen", self)
        self.replace_all_button.setObjectName("replaceAllButton")

        self.cancel_button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.cancel_button.rejected.connect(self._cancel)

        form = QFormLayout()
        form.addRow("Suchen:", self.search_input)
        form.addRow("Ersetzen durch:", self.replace_input)
        form.addRow("Bereich:", self.scope_combo)

        options = QHBoxLayout()
        options.addWidget(self.case_sensitive)
        options.addWidget(self.whole_word)
        options.addWidget(self.regex)

        actions = QHBoxLayout()
        actions.addWidget(self.find_previous_button)
        actions.addWidget(self.find_next_button)
        actions.addWidget(self.replace_button)
        actions.addWidget(self.replace_all_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(options)
        layout.addLayout(actions)
        layout.addWidget(self.status_label)
        layout.addWidget(self.cancel_button)

        self.find_previous_button.clicked.connect(self._emit_find_previous)
        self.find_next_button.clicked.connect(self._emit_find_next)
        self.replace_button.clicked.connect(self._emit_replace)
        self.replace_all_button.clicked.connect(self._emit_replace_all)
        self.search_input.returnPressed.connect(self._emit_find_next)

    def _options(self):
        return (
            self.search_input.text(),
            self.replace_input.text(),
            self.case_sensitive.isChecked(),
            self.whole_word.isChecked(),
            self.regex.isChecked(),
            self.scope_combo.currentData(),
        )

    def _emit_find_next(self):
        query, _, case_sensitive, whole_word, regex, scope = self._options()
        if query:
            self.find_next_requested.emit(query, case_sensitive, whole_word, regex, scope)

    def _emit_find_previous(self):
        query, _, case_sensitive, whole_word, regex, scope = self._options()
        if query:
            self.find_previous_requested.emit(query, case_sensitive, whole_word, regex, scope)

    def _emit_replace(self):
        query, replacement, case_sensitive, whole_word, regex, scope = self._options()
        if query:
            self.replace_requested.emit(
                query, replacement, case_sensitive, whole_word, regex, scope
            )

    def _emit_replace_all(self):
        query, replacement, case_sensitive, whole_word, regex, scope = self._options()
        if query:
            self.replace_all_requested.emit(
                query, replacement, case_sensitive, whole_word, regex, scope
            )

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)

    def focus_replace(self) -> None:
        self.replace_input.setFocus()
        self.replace_input.selectAll()

    def _cancel(self):
        self.cancelled.emit()
        self.hide()

    def closeEvent(self, event):
        self.cancelled.emit()
        super().closeEvent(event)
