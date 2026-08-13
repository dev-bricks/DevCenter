# -*- coding: utf-8 -*-
"""
DevCenter - Code Editor
Syntax-highlighted Python Editor basierend auf PythonBox
"""

import re
import sys
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QPlainTextEdit, QWidget, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, QRect, QSize, Signal, QRegularExpression
from PySide6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QFontMetrics,
    QSyntaxHighlighter, QTextCharFormat, QTextCursor, QPalette,
    QKeySequence, QAction
)


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax Highlighter für Python"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'and', 'as', 'assert', 'async', 'await', 'break', 'class',
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'False', 'try', 'while', 'with', 'yield'
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Builtins
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#dcdcaa"))
        
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr',
            'classmethod', 'compile', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help',
            'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter',
            'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min',
            'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip', '__import__'
        ]
        
        for word in builtins:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, builtin_format))
        
        # Class names (nach 'class')
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4ec9b0"))
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r"\bclass\s+(\w+)"), class_format)
        )
        
        # Function definitions
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#dcdcaa"))
        self.highlighting_rules.append(
            (QRegularExpression(r"\bdef\s+(\w+)"), func_format)
        )
        
        # Self/cls
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#9cdcfe"))
        self_format.setFontItalic(True)
        self.highlighting_rules.append(
            (QRegularExpression(r"\b(self|cls)\b"), self_format)
        )
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append(
            (QRegularExpression(r"\b[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?\b"), number_format)
        )
        
        # Strings (single and double quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )
        self.highlighting_rules.append(
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format)
        )
        
        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#dcdcaa"))
        self.highlighting_rules.append(
            (QRegularExpression(r"@\w+"), decorator_format)
        )
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6a9955"))
        self.highlighting_rules.append(
            (QRegularExpression(r"#[^\n]*"), self.comment_format)
        )
        
        # Multi-line strings
        self.multiline_string_format = QTextCharFormat()
        self.multiline_string_format.setForeground(QColor("#ce9178"))
    
    def highlightBlock(self, text):
        """Highlightet einen Textblock"""
        # Einfache Regeln
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
        
        # Multi-line Strings (docstrings)
        self._highlight_multiline(text, '"""', 1, self.multiline_string_format)
        self._highlight_multiline(text, "'''", 2, self.multiline_string_format)
    
    def _highlight_multiline(self, text, delimiter, state, format):
        """Highlightet Multi-line Strings"""
        if self.previousBlockState() == state:
            start_index = 0
            add = 0
        else:
            start_index = text.find(delimiter)
            add = len(delimiter)
        
        while start_index >= 0:
            end_index = text.find(delimiter, start_index + add)
            
            if end_index == -1:
                self.setCurrentBlockState(state)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + len(delimiter)
            
            self.setFormat(start_index, comment_length, format)
            start_index = text.find(delimiter, start_index + comment_length)


class LineNumberArea(QWidget):
    """Widget für Zeilennummern"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        """Gibt die empfohlene Groesse basierend auf Zeilennummernbreite zurueck."""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """Delegiert das Zeichnen an den Editor."""
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """
    Fortgeschrittener Code-Editor mit:
    - Syntax Highlighting
    - Zeilennummern
    - Aktuelle Zeile hervorheben
    - Auto-Indent
    - Tab-Vervollständigung
    """
    
    # Signals
    file_modified = Signal(bool)
    cursor_position_changed = Signal(int, int)  # line, column
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.file_path: Optional[str] = None
        self._is_modified = False
        self._search_query = ""
        self._search_options: Tuple[bool, bool, bool, str] = (
            False,
            False,
            False,
            "document",
        )
        self._search_matches: List[Tuple[int, int]] = []
        self._search_python_matches: List[Tuple[int, int, re.Match]] = []
        self._search_match_index = -1
        self._search_snapshot = ""
        self._search_scope_python_bounds: Tuple[int, int] = (0, 0)
        self._folded_regions: Dict[int, Tuple[int, ...]] = {}
        
        # Font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Tab-Einstellungen
        self.tab_size = 4
        self.show_line_numbers = True
        self.highlight_current_line_enabled = True
        self.autocomplete_enabled = True
        tab_width = QFontMetrics(font).horizontalAdvance(' ') * self.tab_size
        self.setTabStopDistance(tab_width)
        
        # Appearance
        self._setup_appearance()
        
        # Syntax Highlighting
        self.highlighter = PythonHighlighter(self.document())
        
        # Line Number Area
        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setVisible(self.show_line_numbers)
        
        # Connections
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor_position)
        self.textChanged.connect(self._on_text_changed)
        
        # Initial Setup
        self._update_line_number_area_width(0)
        self._highlight_current_line()
        
        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _setup_appearance(self):
        """Richtet das Erscheinungsbild ein"""
        # Farben
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        self.setPalette(palette)
        
        # Style
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
                selection-color: #ffffff;
                border: none;
            }
        """)
        
        # Word Wrap aus
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    
    def line_number_area_width(self) -> int:
        """Berechnet die Breite des Zeilennummern-Bereichs"""
        if not self.show_line_numbers:
            return 0

        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self, new_block_count):
        """Aktualisiert die Breite des Zeilennummern-Bereichs"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        self.line_number_area.setVisible(self.show_line_numbers)
    
    def _update_line_number_area(self, rect, dy):
        """Aktualisiert den Zeilennummern-Bereich beim Scrollen"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Fenstergrößenänderung"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Zeichnet die Zeilennummern"""
        if not self.show_line_numbers:
            return

        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        current_line = self.textCursor().blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                # Aktuelle Zeile hervorheben
                if block_number == current_line:
                    painter.setPen(QColor("#c6c6c6"))
                else:
                    painter.setPen(QColor("#858585"))
                
                painter.drawText(0, top, self.line_number_area.width() - 5,
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
    
    def _highlight_current_line(self):
        """Hebt die aktuelle Zeile hervor"""
        extra_selections = []
        
        if self.highlight_current_line_enabled and not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)

    def apply_settings(
        self,
        font_family: Optional[str] = None,
        font_size: Optional[int] = None,
        tab_size: Optional[int] = None,
        show_line_numbers: Optional[bool] = None,
        auto_complete: Optional[bool] = None,
        highlight_current_line: Optional[bool] = None,
    ):
        """Wendet Editor-Einstellungen auf diese Instanz an."""
        font = QFont(self.font())

        if font_family is not None:
            font.setFamily(font_family)
        if font_size is not None:
            font.setPointSize(font_size)

        self.setFont(font)

        if tab_size is not None:
            self.tab_size = max(1, int(tab_size))

        tab_width = QFontMetrics(self.font()).horizontalAdvance(' ') * self.tab_size
        self.setTabStopDistance(tab_width)

        if show_line_numbers is not None:
            self.show_line_numbers = bool(show_line_numbers)

        if auto_complete is not None:
            self.autocomplete_enabled = bool(auto_complete)

        if highlight_current_line is not None:
            self.highlight_current_line_enabled = bool(highlight_current_line)

        self._update_line_number_area_width(0)
        self.line_number_area.update()
        self._highlight_current_line()
    
    def _emit_cursor_position(self):
        """Sendet die aktuelle Cursor-Position"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
    
    def _on_text_changed(self):
        """Text wurde geändert"""
        # Folding positions and cached search ranges refer to the previous
        # document.  They are rebuilt lazily after the edit so that a normal
        # typing operation never leaves stale hidden blocks or selections.
        if self._folded_regions:
            self.unfold_all()
        self._folded_regions.clear()
        self._search_matches = []
        self._search_python_matches = []
        self._search_snapshot = ""
        if not self._is_modified:
            self._is_modified = True
            self.file_modified.emit(True)
    
    def keyPressEvent(self, event):
        """Tastatureingabe"""
        # Tab -> Spaces
        if event.key() == Qt.Key.Key_Tab:
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    # Einrücken
                    self._indent_selection(cursor)
                else:
                    # Spaces einfügen
                    cursor.insertText(" " * self.tab_size)
                return
        
        # Shift+Tab -> Unindent
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            self._unindent_selection(cursor)
            return
        
        # Enter -> Auto-Indent
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            line = cursor.block().text()
            
            # Aktuelle Einrückung ermitteln
            indent = ""
            for char in line:
                if char in ' \t':
                    indent += char
                else:
                    break
            
            # Extra Einrückung nach : (if, for, def, class, etc.)
            stripped = line.rstrip()
            if stripped.endswith(':'):
                indent += " " * self.tab_size
            
            # Standard Enter + Auto-Indent
            super().keyPressEvent(event)
            self.textCursor().insertText(indent)
            return
        
        # Backspace am Zeilenanfang -> Unindent
        if event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            if cursor.columnNumber() > 0 and not cursor.hasSelection():
                line = cursor.block().text()
                col = cursor.columnNumber()
                
                # Prüfen ob nur Whitespace vor Cursor
                if line[:col].strip() == "":
                    # Bis zum vorherigen Tab-Stop löschen
                    spaces_to_delete = col % self.tab_size or self.tab_size
                    for _ in range(spaces_to_delete):
                        cursor.deletePreviousChar()
                    return
        
        super().keyPressEvent(event)
    
    def _indent_selection(self, cursor):
        """Rückt die Auswahl ein"""
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.insertText(" " * self.tab_size)
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()
    
    def _unindent_selection(self, cursor):
        """Rückt die Auswahl aus"""
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            
            # Entferne führende Spaces
            spaces_to_remove = 0
            for i, char in enumerate(line):
                if char == ' ' and spaces_to_remove < self.tab_size:
                    spaces_to_remove += 1
                elif char == '\t' and spaces_to_remove == 0:
                    spaces_to_remove = 1
                    break
                else:
                    break
            
            for _ in range(spaces_to_remove):
                cursor.deleteChar()
            
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()
    
    def _show_context_menu(self, position):
        """Zeigt das Kontextmenü"""
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        
        # Zusätzliche Aktionen
        comment_action = QAction("Kommentieren/Entkommentieren", self)
        comment_action.setShortcut(QKeySequence("Ctrl+/"))
        comment_action.triggered.connect(self.toggle_comment)
        menu.addAction(comment_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def toggle_comment(self):
        """Kommentiert/Entkommentiert die ausgewählten Zeilen"""
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        # Prüfen ob alle Zeilen kommentiert sind
        all_commented = True
        check_cursor = QTextCursor(cursor)
        for _ in range(end_block - start_block + 1):
            line = check_cursor.block().text().lstrip()
            if not line.startswith('#'):
                all_commented = False
                break
            check_cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        # Kommentieren oder Entkommentieren
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            
            if all_commented:
                # Entkommentieren
                pos = 0
                for i, char in enumerate(line):
                    if char == '#':
                        pos = i
                        break
                cursor.movePosition(QTextCursor.MoveOperation.Right, n=pos)
                cursor.deleteChar()
                if cursor.block().text()[pos:pos+1] == ' ':
                    cursor.deleteChar()
            else:
                # Kommentieren
                cursor.insertText("# ")
            
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()

    # === Suche und Ersetzen ===

    @staticmethod
    def _utf16_length(value: str) -> int:
        """Gibt die Qt-Positionseinheiten für einen Python-String zurück."""
        return len(value.encode("utf-16-le", "surrogatepass")) // 2

    @classmethod
    def _qt_position_for_python_index(cls, text: str, index: int) -> int:
        """Wandelt einen Python-Stringindex in eine QTextCursor-Position um."""
        return cls._utf16_length(text[:max(0, min(index, len(text)))])

    @classmethod
    def _python_index_for_qt_position(cls, text: str, position: int) -> int:
        """Wandelt eine QTextCursor-Position in einen Python-Stringindex um."""
        if position <= 0:
            return 0
        units = 0
        for index, character in enumerate(text):
            if units >= position:
                return index
            units += cls._utf16_length(character)
            if units >= position:
                return index + 1
        return len(text)

    @staticmethod
    def _search_pattern(query: str, case_sensitive: bool, whole_word: bool,
                        regex: bool) -> re.Pattern:
        flags = 0 if case_sensitive else re.IGNORECASE
        if regex:
            expression = query
            if whole_word:
                expression = rf"(?<!\w)(?:{expression})(?!\w)"
        else:
            expression = re.escape(query)
            if whole_word:
                expression = rf"(?<!\w){expression}(?!\w)"
        return re.compile(expression, flags)

    def _scope_bounds(self, scope: str, text: str) -> Tuple[int, int]:
        """Ermittelt Suchgrenzen in Python-Stringindizes."""
        if scope == "selection":
            cursor = self.textCursor()
            if not cursor.hasSelection():
                return (0, 0)
            return (
                self._python_index_for_qt_position(text, cursor.selectionStart()),
                self._python_index_for_qt_position(text, cursor.selectionEnd()),
            )
        return (0, len(text))

    def _build_search_matches(
        self,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        regex: bool,
        scope: str,
        bounds: Optional[Tuple[int, int]] = None,
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int, re.Match]], Tuple[int, int]]:
        """Berechnet Treffer, ohne den Editor-Cursor zu verändern."""
        text = self.toPlainText()
        bounds = bounds if bounds is not None else self._scope_bounds(scope, text)
        start, end = max(0, bounds[0]), min(len(text), bounds[1])
        if not query or start >= end:
            return [], [], (start, end)

        pattern = self._search_pattern(query, case_sensitive, whole_word, regex)
        qt_matches: List[Tuple[int, int]] = []
        python_matches: List[Tuple[int, int, re.Match]] = []
        segment = text[start:end]
        for match in pattern.finditer(segment):
            # Zero-width matches cannot be selected or replaced meaningfully.
            if match.start() == match.end():
                continue
            py_start = start + match.start()
            py_end = start + match.end()
            qt_matches.append((
                self._qt_position_for_python_index(text, py_start),
                self._qt_position_for_python_index(text, py_end),
            ))
            python_matches.append((py_start, py_end, match))
        return qt_matches, python_matches, (start, end)

    def _resolve_search_options(
        self,
        query: Optional[str],
        case_sensitive: Optional[bool],
        whole_word: Optional[bool],
        regex: Optional[bool],
        scope: Optional[str],
    ) -> Tuple[str, bool, bool, bool, str]:
        if query is None:
            query = self._search_query
        if case_sensitive is None:
            case_sensitive = self._search_options[0]
        if whole_word is None:
            whole_word = self._search_options[1]
        if regex is None:
            regex = self._search_options[2]
        if scope is None:
            scope = self._search_options[3]
        scope = "selection" if str(scope).lower() == "selection" else "document"
        return str(query), bool(case_sensitive), bool(whole_word), bool(regex), scope

    def _prepare_search(
        self,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        regex: bool,
        scope: str,
    ) -> None:
        options = (case_sensitive, whole_word, regex, scope)
        text = self.toPlainText()
        if (
            query != self._search_query
            or options != self._search_options
            or text != self._search_snapshot
        ):
            bounds = self._scope_bounds(scope, text)
            matches, python_matches, bounds = self._build_search_matches(
                query, case_sensitive, whole_word, regex, scope, bounds
            )
            self._search_query = query
            self._search_options = options
            self._search_matches = matches
            self._search_python_matches = python_matches
            self._search_scope_python_bounds = bounds
            self._search_snapshot = text
            self._search_match_index = -1

    def find_matches(
        self,
        query: str,
        *,
        case_sensitive: bool = False,
        whole_word: bool = False,
        regex: bool = False,
        scope: str = "document",
    ) -> List[Tuple[int, int]]:
        """Gibt alle Treffer als ``(Start, Ende)``-Positionen zurück."""
        matches, _, _ = self._build_search_matches(
            query, case_sensitive, whole_word, regex,
            "selection" if str(scope).lower() == "selection" else "document",
        )
        return matches

    # Alias für Integrationen, die die Aktion semantisch als Suche benennen.
    search_all = find_matches

    def _select_search_match(self, index: int) -> bool:
        if index < 0 or index >= len(self._search_matches):
            return False
        start, end = self._search_matches[index]
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self._search_match_index = index
        return True

    def find_next(
        self,
        query: Optional[str] = None,
        *,
        case_sensitive: Optional[bool] = None,
        whole_word: Optional[bool] = None,
        regex: Optional[bool] = None,
        scope: Optional[str] = None,
        wrap: bool = True,
    ) -> bool:
        """Wählt den nächsten Treffer und navigiert zyklisch durch das Dokument."""
        query, case_sensitive, whole_word, regex, scope = self._resolve_search_options(
            query, case_sensitive, whole_word, regex, scope
        )
        self._prepare_search(query, case_sensitive, whole_word, regex, scope)
        if not self._search_matches:
            return False

        cursor = self.textCursor()
        position = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
        index = next(
            (i for i, (start, _) in enumerate(self._search_matches) if start >= position),
            None,
        )
        if index is None:
            if not wrap:
                return False
            index = 0
        return self._select_search_match(index)

    def find_previous(
        self,
        query: Optional[str] = None,
        *,
        case_sensitive: Optional[bool] = None,
        whole_word: Optional[bool] = None,
        regex: Optional[bool] = None,
        scope: Optional[str] = None,
        wrap: bool = True,
    ) -> bool:
        """Wählt den vorherigen Treffer und navigiert zyklisch durch das Dokument."""
        query, case_sensitive, whole_word, regex, scope = self._resolve_search_options(
            query, case_sensitive, whole_word, regex, scope
        )
        self._prepare_search(query, case_sensitive, whole_word, regex, scope)
        if not self._search_matches:
            return False

        cursor = self.textCursor()
        position = cursor.selectionStart() if cursor.hasSelection() else cursor.position()
        index = next(
            (
                i
                for i in range(len(self._search_matches) - 1, -1, -1)
                if self._search_matches[i][1] <= position
            ),
            None,
        )
        if index is None:
            if not wrap:
                return False
            index = len(self._search_matches) - 1
        return self._select_search_match(index)

    # Semantischer Alias für GUI-Integrationen.
    search = find_next

    def search_match_count(self) -> int:
        """Anzahl der Treffer der aktuellen Suchsitzung."""
        return len(self._search_matches)

    def search_match_index(self) -> int:
        """1-basierter Index des aktuellen Treffers, 0 wenn keiner gewählt ist."""
        return self._search_match_index + 1 if self._search_match_index >= 0 else 0

    def _replacement_for_match(self, replacement: str, match: re.Match) -> str:
        if self._search_options[2]:
            return match.expand(replacement)
        return replacement

    def _set_cursor_position_preserving_selection(self, anchor: int, position: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(max(0, anchor))
        if anchor != position:
            cursor.setPosition(max(0, position), QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.setPosition(max(0, position))
        self.setTextCursor(cursor)

    def replace_current(
        self,
        replacement: str,
        query: Optional[str] = None,
        *,
        case_sensitive: Optional[bool] = None,
        whole_word: Optional[bool] = None,
        regex: Optional[bool] = None,
        scope: Optional[str] = None,
    ) -> bool:
        """Ersetzt den aktuell markierten Treffer als eine Undo-Einheit."""
        query, case_sensitive, whole_word, regex, scope = self._resolve_search_options(
            query, case_sensitive, whole_word, regex, scope
        )
        self._prepare_search(query, case_sensitive, whole_word, regex, scope)
        if not self._search_matches:
            return False

        selected = self.textCursor()
        selection = (selected.selectionStart(), selected.selectionEnd())
        try:
            index = self._search_matches.index(selection)
        except ValueError:
            if not self.find_next(query, case_sensitive=case_sensitive,
                                  whole_word=whole_word, regex=regex, scope=scope):
                return False
            index = self._search_match_index

        start, end = self._search_matches[index]
        match = self._search_python_matches[index][2]
        old_match = self._search_python_matches[index]
        try:
            replacement_text = self._replacement_for_match(replacement, match)
        except re.error:
            return False

        cursor = QTextCursor(self.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(replacement_text)
        cursor.endEditBlock()
        cursor.setPosition(start + self._utf16_length(replacement_text))
        self.setTextCursor(cursor)

        old_bounds = self._search_scope_python_bounds
        delta = len(replacement_text) - (old_match[1] - old_match[0])
        if scope == "selection":
            bounds = (
                old_bounds[0],
                old_bounds[1] + delta if old_match[0] < old_bounds[1] else old_bounds[1],
            )
        else:
            bounds = (0, len(self.toPlainText()))
        self._search_snapshot = self.toPlainText()
        self._search_scope_python_bounds = bounds
        self._search_matches, self._search_python_matches, _ = self._build_search_matches(
            query, case_sensitive, whole_word, regex, scope, bounds
        )
        self._search_match_index = -1
        return True

    def replace_all(
        self,
        replacement: str,
        query: Optional[str] = None,
        *,
        case_sensitive: Optional[bool] = None,
        whole_word: Optional[bool] = None,
        regex: Optional[bool] = None,
        scope: Optional[str] = None,
    ) -> int:
        """Ersetzt alle Treffer in einem einzelnen, rückgängig machbaren Edit."""
        query, case_sensitive, whole_word, regex, scope = self._resolve_search_options(
            query, case_sensitive, whole_word, regex, scope
        )
        self._prepare_search(query, case_sensitive, whole_word, regex, scope)
        if not self._search_matches:
            return 0

        search_matches = list(self._search_matches)
        python_matches = list(self._search_python_matches)
        old_bounds = self._search_scope_python_bounds
        replacements: List[Tuple[int, int, str]] = []
        try:
            for (qt_start, qt_end), (py_start, py_end, match) in zip(
                search_matches, python_matches
            ):
                replacements.append((
                    qt_start,
                    qt_end,
                    self._replacement_for_match(replacement, match),
                ))
        except re.error:
            return 0

        old_text = self.toPlainText()
        original_cursor = self.textCursor()
        original_anchor_py = self._python_index_for_qt_position(old_text, original_cursor.anchor())
        original_position_py = self._python_index_for_qt_position(old_text, original_cursor.position())

        cursor = QTextCursor(self.document())
        cursor.beginEditBlock()
        for start, end, replacement_text in reversed(replacements):
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(replacement_text)
        cursor.endEditBlock()

        def adjusted_position(position_py: int) -> int:
            delta = 0
            for (py_start, py_end, _), (_, _, replacement_text) in zip(
                python_matches, replacements
            ):
                if py_end <= position_py:
                    delta += len(replacement_text) - (py_end - py_start)
                elif py_start < position_py:
                    return py_start + delta + len(replacement_text)
            return position_py + delta

        new_anchor = self._qt_position_for_python_index(
            self.toPlainText(), adjusted_position(original_anchor_py)
        )
        new_position = self._qt_position_for_python_index(
            self.toPlainText(), adjusted_position(original_position_py)
        )
        self._set_cursor_position_preserving_selection(new_anchor, new_position)

        if scope == "selection":
            new_bounds = list(old_bounds)
            for py_start, py_end, replacement_text in [
                (match[0], match[1], repl)
                for match, (_, _, repl) in zip(python_matches, replacements)
            ]:
                delta = len(replacement_text) - (py_end - py_start)
                if py_start < new_bounds[1]:
                    new_bounds[1] += delta
            bounds = (new_bounds[0], new_bounds[1])
        else:
            bounds = (0, len(self.toPlainText()))

        self._search_snapshot = self.toPlainText()
        self._search_scope_python_bounds = bounds
        self._search_matches, self._search_python_matches, _ = self._build_search_matches(
            query, case_sensitive, whole_word, regex, scope, bounds
        )
        self._search_match_index = -1
        return len(replacements)

    def cancel_search(self) -> None:
        """Beendet die Suchsitzung ohne Text- oder Tab-Mutation."""
        self._search_query = ""
        self._search_matches = []
        self._search_python_matches = []
        self._search_snapshot = ""
        self._search_match_index = -1

    # === Code-Folding ===

    def _indent_width(self, text: str) -> int:
        """Ermittelt eine vergleichbare Einrückungsbreite für Leerzeichen/Tabs."""
        prefix = text[:len(text) - len(text.lstrip(" \t"))]
        return len(prefix.expandtabs(self.tab_size))

    def _fold_body(self, start_block):
        base_indent = self._indent_width(start_block.text())
        body = []
        block = start_block.next()
        has_child = False
        while block.isValid():
            text = block.text()
            if text.strip() and self._indent_width(text) <= base_indent:
                break
            body.append(block)
            if text.strip():
                has_child = True
            block = block.next()
        return body if has_child else []

    def _request_fold_update(self, start_block, end_block) -> None:
        self.document().markContentsDirty(
            start_block.position(),
            max(1, end_block.position() - start_block.position() + len(end_block.text())),
        )
        self.document().documentLayout().requestUpdate()
        self.viewport().update()
        self.line_number_area.update()

    def foldable_block_numbers(self) -> List[int]:
        """Gibt Zeilen mit mindestens einem eingerückten Folgeblock zurück."""
        result = []
        block = self.document().firstBlock()
        while block.isValid():
            if self._fold_body(block):
                result.append(block.blockNumber())
            block = block.next()
        return result

    def is_folded(self, line_number: int) -> bool:
        block = self.document().findBlockByNumber(line_number)
        return block.isValid() and block.position() in self._folded_regions

    def fold_block(self, line_number: Optional[int] = None) -> bool:
        """Faltet den Block der 0-basierten Zeilennummer ein."""
        if line_number is None:
            line_number = self.textCursor().blockNumber()
        start_block = self.document().findBlockByNumber(int(line_number))
        if not start_block.isValid() or self.is_folded(start_block.blockNumber()):
            return False
        body = self._fold_body(start_block)
        if not body:
            return False

        body_positions = tuple(block.position() for block in body)
        body_position_set = set(body_positions)
        # Eine äußere Faltung übernimmt den Bereich vollständig; verschachtelte
        # Zustände werden entfernt und beim Unfold nicht versehentlich reaktiviert.
        for nested_start in list(self._folded_regions):
            if nested_start in body_position_set:
                self._restore_fold(nested_start)

        for block in body:
            block.setVisible(False)
            block.setLineCount(0)
        start_block.setVisible(True)
        start_block.setLineCount(1)
        self._folded_regions[start_block.position()] = body_positions
        self._request_fold_update(start_block, body[-1])
        return True

    def _restore_fold(self, start_position: int) -> bool:
        body_positions = self._folded_regions.pop(start_position, None)
        if body_positions is None:
            return False
        start_block = self.document().findBlock(start_position)
        if not start_block.isValid():
            return False
        for position in body_positions:
            block = self.document().findBlock(position)
            if block.isValid():
                block.setVisible(True)
                block.setLineCount(1)
        start_block.setVisible(True)
        start_block.setLineCount(1)
        last_block = self.document().findBlock(body_positions[-1]) if body_positions else start_block
        self._request_fold_update(start_block, last_block)
        return True

    def unfold_block(self, line_number: Optional[int] = None) -> bool:
        """Entfaltet den Block der 0-basierten Zeilennummer."""
        if line_number is None:
            line_number = self.textCursor().blockNumber()
        start_block = self.document().findBlockByNumber(int(line_number))
        if not start_block.isValid():
            return False
        return self._restore_fold(start_block.position())

    def toggle_fold(self, line_number: Optional[int] = None) -> bool:
        """Schaltet Faltung für den aktuellen bzw. angegebenen Block um."""
        if line_number is None:
            line_number = self.textCursor().blockNumber()
        if self.is_folded(int(line_number)):
            return self.unfold_block(int(line_number))
        return self.fold_block(int(line_number))

    def unfold_all(self) -> None:
        """Stellt alle zuvor verborgenen Blöcke wieder her."""
        for start_position in list(self._folded_regions):
            self._restore_fold(start_position)

    def load_file(self, file_path: str) -> bool:
        """
        Lädt eine Datei in den Editor
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            True bei Erfolg
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.unfold_all()
            self._folded_regions.clear()
            self._is_modified = True  # verhindert spurious file_modified(True) durch setPlainText
            self.setPlainText(content)
            self.file_path = file_path
            self._is_modified = False
            self.file_modified.emit(False)
            return True
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def save_file(self, file_path: str = None) -> bool:
        """
        Speichert den Editor-Inhalt
        
        Args:
            file_path: Optional - neuer Speicherpfad
            
        Returns:
            True bei Erfolg
        """
        path = file_path or self.file_path
        
        if not path:
            return False
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            
            self.file_path = path
            self._is_modified = False
            self.file_modified.emit(False)
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    
    def get_text(self) -> str:
        """Gibt den Text zurück"""
        return self.toPlainText()
    
    def is_modified(self) -> bool:
        """Prüft ob der Text geändert wurde"""
        return self._is_modified
    
    def go_to_line(self, line: int):
        """Springt zu einer bestimmten Zeile"""
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)
            self.centerCursor()


if __name__ == "__main__":
    # Test
    app = QApplication(sys.argv)
    
    editor = CodeEditor()
    editor.setPlainText('''# -*- coding: utf-8 -*-
"""Test-Modul für den Code Editor"""

import os
from pathlib import Path

class TestClass:
    """Eine Test-Klasse"""
    
    def __init__(self, name: str):
        self.name = name
        self.value = 42
    
    def greet(self):
        """Begrüßung ausgeben"""
        print(f"Hello, {self.name}!")
        return True

def main():
    obj = TestClass("World")
    obj.greet()
    
    # Ein Kommentar
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"Sum: {total}")

if __name__ == "__main__":
    main()
''')
    
    editor.resize(800, 600)
    editor.show()
    
    sys.exit(app.exec())
