# -*- coding: utf-8 -*-
"""
DevCenter - Explorer Panel
Datei-Navigation und Projekt-Struktur
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLineEdit,
    QPushButton, QMenu, QLabel, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QDir, QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileSystemModel


class ExplorerPanel(QWidget):
    """
    Datei-Explorer Panel
    
    Features:
    - Projekt-Struktur anzeigen
    - Dateifilter
    - Kontextmenü
    - Schnelle Navigation
    """
    
    file_selected = Signal(str)  # Datei zum Öffnen
    file_renamed = Signal(str, str)  # alt, neu
    file_deleted = Signal(str)
    folder_created = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_path = ""
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QHBoxLayout()
        header.setContentsMargins(4, 4, 4, 4)
        
        self.title_label = QLabel("📁 EXPLORER")
        self.title_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Aktualisieren")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.clicked.connect(self._refresh)
        header.addWidget(self.refresh_btn)
        
        self.collapse_btn = QPushButton("⬆")
        self.collapse_btn.setToolTip("Alle zuklappen")
        self.collapse_btn.setMaximumWidth(30)
        self.collapse_btn.clicked.connect(self._collapse_all)
        header.addWidget(self.collapse_btn)
        
        layout.addLayout(header)
        
        # Filter
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 Dateien filtern...")
        self.filter_input.textChanged.connect(self._apply_filter)
        self.filter_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #cccccc;
                border: none;
                padding: 4px 8px;
                margin: 2px 4px;
            }
        """)
        layout.addWidget(self.filter_input)
        
        # Tree View
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.doubleClicked.connect(self._on_double_click)
        
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 2px;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(:/icons/branch-closed.png);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(:/icons/branch-open.png);
            }
        """)
        
        # File System Model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        
        # Filter: Nur relevante Dateien
        self.model.setNameFilters([
            "*.py", "*.pyw", "*.txt", "*.md", "*.json", "*.xml",
            "*.html", "*.css", "*.js", "*.yml", "*.yaml", "*.ini",
            "*.cfg", "*.toml", "*.rst", "*.bat", "*.sh", "*.sql"
        ])
        self.model.setNameFilterDisables(False)
        
        self.tree.setModel(self.model)
        
        # Nur Name-Spalte anzeigen
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)
        
        layout.addWidget(self.tree)
    
    def set_root_path(self, path: str):
        """Setzt das Wurzelverzeichnis"""
        if os.path.exists(path):
            self._root_path = path
            self.model.setRootPath(path)
            self.tree.setRootIndex(self.model.index(path))
            
            # Titel aktualisieren
            project_name = os.path.basename(path)
            self.title_label.setText(f"📁 {project_name.upper()}")
    
    def get_selected_path(self) -> str:
        """Gibt den ausgewählten Pfad zurück"""
        indexes = self.tree.selectedIndexes()
        if indexes:
            return self.model.filePath(indexes[0])
        return ""
    
    def _refresh(self):
        """Aktualisiert die Ansicht"""
        if self._root_path:
            self.model.setRootPath("")
            self.model.setRootPath(self._root_path)
    
    def _collapse_all(self):
        """Klappt alle Knoten zu"""
        self.tree.collapseAll()
    
    def _apply_filter(self, text: str):
        """Wendet Dateifilter an"""
        if text:
            # Dynamischer Filter
            patterns = [f"*{text}*"]
            self.model.setNameFilters(patterns)
        else:
            # Standard-Filter
            self.model.setNameFilters([
                "*.py", "*.pyw", "*.txt", "*.md", "*.json", "*.xml",
                "*.html", "*.css", "*.js", "*.yml", "*.yaml", "*.ini",
                "*.cfg", "*.toml", "*.rst", "*.bat", "*.sh", "*.sql"
            ])
    
    def _on_double_click(self, index: QModelIndex):
        """Behandelt Doppelklick"""
        path = self.model.filePath(index)
        
        if os.path.isfile(path):
            self.file_selected.emit(path)
    
    def _show_context_menu(self, position):
        """Zeigt Kontextmenü"""
        index = self.tree.indexAt(position)
        path = self.model.filePath(index) if index.isValid() else self._root_path
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3c3c3c;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        
        if os.path.isfile(path):
            # Datei-Menü
            open_action = menu.addAction("📂 Öffnen")
            open_action.triggered.connect(lambda: self.file_selected.emit(path))
            
            menu.addSeparator()
            
            rename_action = menu.addAction("✏️ Umbenennen")
            rename_action.triggered.connect(lambda: self._rename_file(path))
            
            delete_action = menu.addAction("🗑️ Löschen")
            delete_action.triggered.connect(lambda: self._delete_file(path))
            
            menu.addSeparator()
            
            copy_path_action = menu.addAction("📋 Pfad kopieren")
            copy_path_action.triggered.connect(lambda: self._copy_path(path))
            
        else:
            # Ordner-Menü
            new_file_action = menu.addAction("📄 Neue Datei")
            new_file_action.triggered.connect(lambda: self._new_file(path))
            
            new_folder_action = menu.addAction("📁 Neuer Ordner")
            new_folder_action.triggered.connect(lambda: self._new_folder(path))
            
            menu.addSeparator()
            
            if path != self._root_path:
                rename_action = menu.addAction("✏️ Umbenennen")
                rename_action.triggered.connect(lambda: self._rename_folder(path))
                
                delete_action = menu.addAction("🗑️ Löschen")
                delete_action.triggered.connect(lambda: self._delete_folder(path))
            
            menu.addSeparator()
            
            open_explorer_action = menu.addAction("📂 Im Explorer öffnen")
            open_explorer_action.triggered.connect(lambda: self._open_in_explorer(path))
        
        menu.exec(self.tree.viewport().mapToGlobal(position))
    
    def _rename_file(self, path: str):
        """Datei umbenennen"""
        name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(
            self, "Umbenennen", "Neuer Name:", text=name
        )
        
        if ok and new_name and new_name != name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self.file_renamed.emit(path, new_path)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Umbenennen fehlgeschlagen: {e}")
    
    def _delete_file(self, path: str):
        """Datei löschen"""
        reply = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Datei '{os.path.basename(path)}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(path)
                self.file_deleted.emit(path)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Löschen fehlgeschlagen: {e}")
    
    def _new_file(self, folder: str):
        """Neue Datei erstellen"""
        name, ok = QInputDialog.getText(
            self, "Neue Datei", "Dateiname:"
        )
        
        if ok and name:
            path = os.path.join(folder, name)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("")
                self._refresh()
                self.file_selected.emit(path)
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Erstellen fehlgeschlagen: {e}")
    
    def _new_folder(self, parent: str):
        """Neuen Ordner erstellen"""
        name, ok = QInputDialog.getText(
            self, "Neuer Ordner", "Ordnername:"
        )
        
        if ok and name:
            path = os.path.join(parent, name)
            try:
                os.makedirs(path, exist_ok=True)
                self.folder_created.emit(path)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Erstellen fehlgeschlagen: {e}")
    
    def _rename_folder(self, path: str):
        """Ordner umbenennen"""
        name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(
            self, "Umbenennen", "Neuer Name:", text=name
        )
        
        if ok and new_name and new_name != name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Umbenennen fehlgeschlagen: {e}")
    
    def _delete_folder(self, path: str):
        """Ordner löschen"""
        reply = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Ordner '{os.path.basename(path)}' und alle Inhalte wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import shutil
            try:
                shutil.rmtree(path)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Löschen fehlgeschlagen: {e}")
    
    def _copy_path(self, path: str):
        """Kopiert Pfad in Zwischenablage"""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(path)
    
    def _open_in_explorer(self, path: str):
        """Öffnet im System-Explorer"""
        import subprocess
        import sys
        
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', path])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
