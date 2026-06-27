# -*- coding: utf-8 -*-
"""
DevCenter - AI Assistant Panel
Chat-Interface für Code-Generierung und Hilfe
"""

import asyncio
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPlainTextEdit,
    QPushButton, QLabel, QComboBox, QSplitter, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QFont, QTextCursor
from typing import Optional
from modules.ai_assistant.ai_service import AIModel


_MODEL_MAP = [AIModel.CLAUDE_SONNET, AIModel.CLAUDE_OPUS, AIModel.CLAUDE_HAIKU]


class AIWorker(QThread):
    """Worker Thread für AI-Anfragen"""
    
    response_received = Signal(str, bool)  # content, success
    progress_update = Signal(str)
    
    def __init__(self, ai_service, prompt: str, system: str = None):
        super().__init__()
        self.ai_service = ai_service
        self.prompt = prompt
        self.system = system
    
    def run(self):
        """Fuehrt die AI-Anfrage im Hintergrund aus."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                self.ai_service.complete(self.prompt, self.system)
            )
            if response.success:
                self.response_received.emit(response.content, True)
            else:
                self.response_received.emit(response.error or "Unbekannter Fehler", False)
        except Exception as e:
            self.response_received.emit(str(e), False)
        finally:
            loop.close()
            asyncio.set_event_loop(None)


class AIAssistantPanel(QWidget):
    """
    AI-Assistenz Panel
    
    Features:
    - Chat-Interface
    - Code-Generierung
    - Kontext aus aktuellem Editor
    - Verlauf
    """
    
    code_generated = Signal(str)  # Generierter Code
    insert_code_requested = Signal(str)  # Code zum Einfügen
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ai_service = None
        self._worker: Optional[AIWorker] = None
        self._context_code = ""
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("🤖 AI Assistent"))
        header.addStretch()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Claude Sonnet", "Claude Opus", "Claude Haiku"])
        self.model_combo.setCurrentIndex(0)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        header.addWidget(self.model_combo)
        
        layout.addLayout(header)
        
        # Splitter für Chat und Input
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Chat-Verlauf
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
        """)
        self.chat_display.setHtml(self._get_welcome_html())
        splitter.addWidget(self.chat_display)
        
        # Input-Bereich
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText("Beschreibe was du brauchst...")
        self.input_text.setFont(QFont("Consolas", 10))
        self.input_text.setMaximumHeight(100)
        self.input_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
        """)
        input_layout.addWidget(self.input_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.context_label = QLabel("Kein Kontext")
        self.context_label.setStyleSheet("color: #888; font-size: 11px;")
        btn_layout.addWidget(self.context_label)
        
        btn_layout.addStretch()
        
        self.generate_btn = QPushButton("✨ Generieren")
        self.generate_btn.clicked.connect(self._on_generate)
        btn_layout.addWidget(self.generate_btn)
        
        self.review_btn = QPushButton("🔍 Review")
        self.review_btn.clicked.connect(self._on_review)
        btn_layout.addWidget(self.review_btn)
        
        self.explain_btn = QPushButton("📖 Erklären")
        self.explain_btn.clicked.connect(self._on_explain)
        btn_layout.addWidget(self.explain_btn)
        
        input_layout.addLayout(btn_layout)
        
        splitter.addWidget(input_widget)
        splitter.setSizes([300, 150])
        
        layout.addWidget(splitter)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(3)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #252526;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        layout.addWidget(self.progress)
    
    def _get_welcome_html(self) -> str:
        return """
        <div style="color: #888; padding: 10px;">
            <h3 style="color: #cccccc;">Willkommen beim AI-Assistenten!</h3>
            <p>Ich kann dir helfen mit:</p>
            <ul>
                <li>Code generieren aus Beschreibungen</li>
                <li>Code reviewen und verbessern</li>
                <li>Code erklären</li>
                <li>Fehler beheben</li>
            </ul>
            <p><i>Wähle Code im Editor aus für Kontext.</i></p>
        </div>
        """
    
    def set_ai_service(self, ai_service):
        """Setzt den AI-Service"""
        self._ai_service = ai_service

        if ai_service and ai_service.is_available():
            self.generate_btn.setEnabled(True)
            self.review_btn.setEnabled(True)
            self.explain_btn.setEnabled(True)
        else:
            self.generate_btn.setEnabled(False)
            self.review_btn.setEnabled(False)
            self.explain_btn.setEnabled(False)

        # Aktuell ausgewähltes Modell sofort synchronisieren
        self._on_model_changed(self.model_combo.currentIndex())

    @Slot(int)
    def _on_model_changed(self, index: int):
        """Aktualisiert das AI-Modell wenn der Nutzer die Auswahl ändert."""
        if self._ai_service and 0 <= index < len(_MODEL_MAP):
            self._ai_service.set_model(_MODEL_MAP[index])
    
    def set_context(self, code: str, file_name: str = ""):
        """Setzt den Code-Kontext aus dem Editor"""
        self._context_code = code
        
        if code:
            lines = len(code.split('\n'))
            self.context_label.setText(f"📄 {file_name or 'Auswahl'} ({lines} Zeilen)")
            self.context_label.setStyleSheet("color: #4ec9b0; font-size: 11px;")
        else:
            self.context_label.setText("Kein Kontext")
            self.context_label.setStyleSheet("color: #888; font-size: 11px;")
    
    def _start_request(self, prompt: str, system: str = None):
        """Startet eine AI-Anfrage"""
        if not self._ai_service or not self._ai_service.is_available():
            self._add_error("AI-Service nicht verfügbar. API-Key in Einstellungen prüfen.")
            return
        
        if self._worker and self._worker.isRunning():
            self._add_error("Eine Anfrage läuft bereits...")
            return
        
        self._set_loading(True)
        self._add_user_message(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        
        if self._worker is not None:
            try:
                self._worker.response_received.disconnect(self._on_response)
            except RuntimeError:
                pass
        self._worker = AIWorker(self._ai_service, prompt, system)
        self._worker.response_received.connect(self._on_response)
        self._worker.start()
    
    @Slot(str, bool)
    def _on_response(self, content: str, success: bool):
        """Verarbeitet AI-Antwort"""
        if self.sender() is not self._worker:
            return
        self._set_loading(False)
        
        if success:
            self._add_assistant_message(content)
            
            # Code extrahieren wenn vorhanden
            if "```" in content:
                import re
                code_blocks = re.findall(r'```(?:python)?\n(.*?)```', content, re.DOTALL)
                if code_blocks:
                    self.code_generated.emit(code_blocks[0])
        else:
            self._add_error(content)
    
    def _set_loading(self, loading: bool):
        """Setzt Loading-Status"""
        self.progress.setVisible(loading)
        if loading:
            self.progress.setRange(0, 0)  # Indeterminate
        
        self.generate_btn.setEnabled(not loading)
        self.review_btn.setEnabled(not loading)
        self.explain_btn.setEnabled(not loading)
    
    def _add_user_message(self, text: str):
        """Fügt Benutzer-Nachricht hinzu"""
        html = f"""
        <div style="background-color: #094771; padding: 8px; margin: 4px 0; border-radius: 4px;">
            <b style="color: #4ec9b0;">Du:</b>
            <p style="color: #cccccc; margin: 4px 0;">{self._escape_html(text)}</p>
        </div>
        """
        self._append_html(html)
    
    def _add_assistant_message(self, text: str):
        """Fügt Assistenten-Nachricht hinzu"""
        # Code-Blöcke formatieren
        formatted = self._format_code_blocks(text)
        
        html = f"""
        <div style="background-color: #252526; padding: 8px; margin: 4px 0; border-radius: 4px;">
            <b style="color: #569cd6;">Assistent:</b>
            <div style="color: #cccccc; margin: 4px 0;">{formatted}</div>
        </div>
        """
        self._append_html(html)
    
    def _add_error(self, text: str):
        """Fügt Fehler-Nachricht hinzu"""
        html = f"""
        <div style="background-color: #5a1d1d; padding: 8px; margin: 4px 0; border-radius: 4px;">
            <b style="color: #f44747;">Fehler:</b>
            <p style="color: #cccccc; margin: 4px 0;">{self._escape_html(text)}</p>
        </div>
        """
        self._append_html(html)
    
    def _append_html(self, html: str):
        """Fügt HTML zum Chat hinzu"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _escape_html(self, text: str) -> str:
        """Escaped HTML-Zeichen"""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    
    def _format_code_blocks(self, text: str) -> str:
        """Formatiert Code-Blöcke — nicht-Code-Text wird HTML-escaped."""
        import re

        # Text in Code-Blöcke und normalen Text aufteilen
        parts = re.split(r'(```(?:python)?\n.*?```)', text, flags=re.DOTALL)
        result_parts = []

        for part in parts:
            m = re.match(r'```(?:python)?\n(.*?)```', part, re.DOTALL)
            if m:
                code = m.group(1)
                result_parts.append(
                    f'<pre style="background-color: #1e1e1e; padding: 8px; border-radius: 4px;'
                    f' font-family: Consolas; overflow-x: auto;">{self._escape_html(code)}</pre>'
                )
            else:
                # Inline-Code innerhalb des normalen Texts separat behandeln
                inline_parts = re.split(r'(`[^`\n]+`)', part)
                for ip in inline_parts:
                    if ip.startswith('`') and ip.endswith('`') and len(ip) > 2:
                        result_parts.append(
                            f'<code style="background-color: #1e1e1e; padding: 2px 4px;">'
                            f'{self._escape_html(ip[1:-1])}</code>'
                        )
                    else:
                        result_parts.append(self._escape_html(ip).replace("\n", "<br>"))

        return "".join(result_parts)
    
    def _on_generate(self):
        """Code generieren"""
        prompt = self.input_text.toPlainText().strip()
        if not prompt:
            self._add_error("Bitte gib eine Beschreibung ein.")
            return
        
        full_prompt = f"Generiere Python-Code für: {prompt}"
        
        if self._context_code:
            full_prompt += f"\n\nBestehender Code als Kontext:\n```python\n{self._context_code}\n```"
        
        self._start_request(full_prompt)
        self.input_text.clear()
    
    def _on_review(self):
        """Code reviewen"""
        if not self._context_code:
            self._add_error("Bitte wähle Code im Editor aus.")
            return
        
        prompt = f"Bitte reviewe folgenden Python-Code und gib Verbesserungsvorschläge:\n\n```python\n{self._context_code}\n```"
        self._start_request(prompt)
    
    def _on_explain(self):
        """Code erklären"""
        if not self._context_code:
            self._add_error("Bitte wähle Code im Editor aus.")
            return
        
        prompt = f"Bitte erkläre folgenden Python-Code Schritt für Schritt:\n\n```python\n{self._context_code}\n```"
        self._start_request(prompt)
    
    def clear_chat(self):
        """Leert den Chat-Verlauf"""
        self.chat_display.setHtml(self._get_welcome_html())
        if self._ai_service:
            self._ai_service.clear_history()

    def stop(self):
        """Beendet einen laufenden Worker-Thread sauber (für closeEvent).

        AIWorker.run() blockiert in asyncio.run_until_complete() und hat keinen
        Qt-Event-Loop — quit() ist daher wirkungslos. Wir warten bounded (3 s) und
        nutzen terminate() als Fallback, damit das Fenster nicht hängt.
        """
        if self._worker is not None and self._worker.isRunning():
            self._worker.quit()  # No-op ohne Event-Loop, aber schadet nicht
            if not self._worker.wait(3000):
                self._worker.terminate()
                self._worker.wait()
