# -*- coding: utf-8 -*-
"""Nicht-modaler Dialog für die Editor-Suche und das Ersetzen."""

from PySide6.QtCore import QEvent, Qt, Signal
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

        self.search_label = QLabel("&Suchen:", self)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Suchbegriff")
        self.search_input.setToolTip("Suchbegriff eingeben (Alt+S)")
        self.search_input.setAccessibleName("Suchbegriff")
        self.search_input.setAccessibleDescription("Suchbegriff für das aktive Dokument oder die Auswahl")
        self.search_label.setBuddy(self.search_input)

        self.replace_label = QLabel("E&rsetzen durch:", self)
        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Ersetzung (leer erlaubt)")
        self.replace_input.setToolTip("Ersetzungstext eingeben (Alt+R)")
        self.replace_input.setAccessibleName("Ersetzung")
        self.replace_input.setAccessibleDescription("Text, durch den Treffer ersetzt werden sollen")
        self.replace_label.setBuddy(self.replace_input)

        self.case_sensitive = QCheckBox("&Groß-/Kleinschreibung beachten", self)
        self.case_sensitive.setToolTip("Groß- und Kleinschreibung genau beachten")
        self.case_sensitive.setAccessibleName("Groß-/Kleinschreibung beachten")
        self.case_sensitive.setAccessibleDescription("Wenn aktiviert, werden Groß- und Kleinbuchstaben exakt unterschieden")

        self.whole_word = QCheckBox("Nur ganze &Wörter", self)
        self.whole_word.setToolTip("Nur vollständige Wörter als Treffer werten")
        self.whole_word.setAccessibleName("Nur ganze Wörter")
        self.whole_word.setAccessibleDescription("Wenn aktiviert, werden Wortbestandteile ignoriert")

        self.regex = QCheckBox("Regulärer Ausdr&uck", self)
        self.regex.setToolTip("Suchbegriff als regulären Python-Ausdruck auswerten")
        self.regex.setAccessibleName("Regulärer Ausdruck")
        self.regex.setAccessibleDescription("Wenn aktiviert, wird der Suchbegriff als regulärer Python-Ausdruck interpretiert")

        self.scope_label = QLabel("&Bereich:", self)
        self.scope_combo = QComboBox(self)
        self.scope_combo.addItem("Gesamtes Dokument", "document")
        self.scope_combo.addItem("Aktuelle Auswahl", "selection")
        self.scope_combo.setToolTip("Suchbereich auswählen (Alt+B)")
        self.scope_combo.setAccessibleName("Suchbereich")
        self.scope_combo.setAccessibleDescription("Legt fest, ob im gesamten Dokument oder nur in der aktuellen Auswahl gesucht wird")
        self.scope_label.setBuddy(self.scope_combo)

        self.status_label = QLabel("", self)
        self.status_label.setWordWrap(True)
        self.status_label.setAccessibleName("Suchstatus")
        self.status_label.setAccessibleDescription("Aktuelle Rückmeldung zur Suche oder Ersetzung")

        self.find_previous_button = QPushButton("&Vorheriger Treffer", self)
        self.find_previous_button.setObjectName("findPreviousButton")
        self.find_previous_button.setShortcut("Shift+F3")
        self.find_previous_button.setToolTip("Vorherigen Treffer anspringen (Umschalt+Eingabetaste / Alt+V / Umschalt+F3)")
        self.find_previous_button.setAccessibleName("Vorherigen Treffer suchen")
        self.find_previous_button.setAccessibleDescription("Springt zum vorherigen Vorkommen des Suchbegriffs")

        self.find_next_button = QPushButton("&Nächster Treffer", self)
        self.find_next_button.setObjectName("findNextButton")
        self.find_next_button.setShortcut("F3")
        self.find_next_button.setToolTip("Nächsten Treffer anspringen (Eingabetaste / Alt+N / F3)")
        self.find_next_button.setAccessibleName("Nächsten Treffer suchen")
        self.find_next_button.setAccessibleDescription("Springt zum nächsten Vorkommen des Suchbegriffs")

        self.replace_button = QPushButton("&Ersetzen", self)
        self.replace_button.setObjectName("replaceButton")
        self.replace_button.setToolTip("Aktuellen Treffer ersetzen (Eingabetaste im Ersetzen-Feld oder Alt+E)")
        self.replace_button.setAccessibleName("Aktuellen Treffer ersetzen")
        self.replace_button.setAccessibleDescription("Ersetzt die aktuelle Fundstelle durch den Ersetzungstext")

        self.replace_all_button = QPushButton("&Alle ersetzen", self)
        self.replace_all_button.setObjectName("replaceAllButton")
        self.replace_all_button.setToolTip("Alle Treffer im gewählten Bereich ersetzen (Alt+A)")
        self.replace_all_button.setAccessibleName("Alle Treffer ersetzen")
        self.replace_all_button.setAccessibleDescription("Ersetzt alle Vorkommen des Suchbegriffs im gewählten Bereich")

        self.cancel_button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.cancel_button.setToolTip("Suchdialog schließen (Escape)")
        self.cancel_button.setAccessibleName("Suchdialog schließen")
        self.cancel_button.rejected.connect(self._cancel)

        form = QFormLayout()
        form.addRow(self.search_label, self.search_input)
        form.addRow(self.replace_label, self.replace_input)
        form.addRow(self.scope_label, self.scope_combo)

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

        self.setTabOrder(self.search_input, self.replace_input)
        self.setTabOrder(self.replace_input, self.scope_combo)
        self.setTabOrder(self.scope_combo, self.case_sensitive)
        self.setTabOrder(self.case_sensitive, self.whole_word)
        self.setTabOrder(self.whole_word, self.regex)
        self.setTabOrder(self.regex, self.find_next_button)
        self.setTabOrder(self.find_next_button, self.find_previous_button)
        self.setTabOrder(self.find_previous_button, self.replace_button)
        self.setTabOrder(self.replace_button, self.replace_all_button)
        self.setTabOrder(self.replace_all_button, self.cancel_button)

        self.find_previous_button.clicked.connect(self._emit_find_previous)
        self.find_next_button.clicked.connect(self._emit_find_next)
        self.replace_button.clicked.connect(self._emit_replace)
        self.replace_all_button.clicked.connect(self._emit_replace_all)
        self.search_input.returnPressed.connect(self._emit_find_next)
        self.replace_input.returnPressed.connect(self._emit_replace)

        self.search_input.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched == self.search_input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self._emit_find_previous()
                    return True
        return super().eventFilter(watched, event)

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

    def reject(self):
        self._cancel()

    def closeEvent(self, event):
        self.cancelled.emit()
        super().closeEvent(event)
