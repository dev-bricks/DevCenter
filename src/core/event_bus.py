# -*- coding: utf-8 -*-
"""
DevCenter - Event Bus
Zentrale Ereignisverwaltung für Modul-Kommunikation
"""

from typing import Callable, Dict, List, Any
from PySide6.QtCore import QObject, Signal, QThread, Qt
from enum import Enum, auto


class EventType(Enum):
    """Vordefinierte Event-Typen"""
    # Editor Events
    FILE_OPENED = auto()
    FILE_SAVED = auto()
    FILE_CLOSED = auto()
    FILE_MODIFIED = auto()
    CURSOR_MOVED = auto()
    SELECTION_CHANGED = auto()
    
    # Project Events
    PROJECT_OPENED = auto()
    PROJECT_CLOSED = auto()
    PROJECT_CREATED = auto()
    
    # Analysis Events
    ANALYSIS_STARTED = auto()
    ANALYSIS_COMPLETED = auto()
    ERRORS_FOUND = auto()
    WARNINGS_FOUND = auto()
    
    # Build Events
    BUILD_STARTED = auto()
    BUILD_PROGRESS = auto()
    BUILD_COMPLETED = auto()
    BUILD_FAILED = auto()
    
    # AI Events
    AI_REQUEST_STARTED = auto()
    AI_RESPONSE_RECEIVED = auto()
    AI_ERROR = auto()
    CODE_GENERATED = auto()
    
    # Sync Events
    SYNC_STARTED = auto()
    SYNC_COMPLETED = auto()
    SYNC_ERROR = auto()
    
    # UI Events
    THEME_CHANGED = auto()
    SETTINGS_CHANGED = auto()
    STATUS_MESSAGE = auto()
    SHOW_NOTIFICATION = auto()


class Event:
    """Event-Datenklasse"""
    
    def __init__(self, event_type: EventType, data: Any = None, 
                 source: str = None):
        self.type = event_type
        self.data = data
        self.source = source
        self.handled = False
    
    def __repr__(self):
        return f"Event({self.type.name}, source={self.source})"


class EventBus(QObject):
    """
    Zentraler Event-Bus für Modul-Kommunikation
    
    Ermöglicht lose Kopplung zwischen Modulen durch
    Publish-Subscribe Pattern.
    
    WICHTIG: Nicht direkt instanziieren! Nutze get_event_bus().
    
    Signals:
        event_emitted: Allgemeines Signal für alle Events
    """
    
    event_emitted = Signal(object)  # Event
    _callback_requested = Signal(object, object)  # callback, Event
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._global_subscribers: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history = 100
        self._callback_requested.connect(
            self._dispatch_queued_callback,
            Qt.ConnectionType.QueuedConnection,
        )
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Registriert einen Callback für einen Event-Typ
        
        Args:
            event_type: Der zu beobachtende Event-Typ
            callback: Funktion die aufgerufen wird (erhält Event als Parameter)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
    
    def subscribe_all(self, callback: Callable):
        """
        Registriert einen Callback für alle Events
        
        Args:
            callback: Funktion die aufgerufen wird (erhält Event als Parameter)
        """
        if callback not in self._global_subscribers:
            self._global_subscribers.append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Entfernt einen Callback für einen Event-Typ
        
        Args:
            event_type: Der Event-Typ
            callback: Der zu entfernende Callback
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    def unsubscribe_all(self, callback: Callable):
        """Entfernt einen globalen Callback"""
        try:
            self._global_subscribers.remove(callback)
        except ValueError:
            pass
    
    def emit(self, event_type: EventType, data: Any = None, 
             source: str = None):
        """
        Sendet ein Event an alle Subscriber
        
        Args:
            event_type: Der Event-Typ
            data: Optionale Event-Daten
            source: Optionaler Quellname
        """
        event = Event(event_type, data, source)
        
        # In History speichern
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Spezifische Subscriber benachrichtigen (Kopie, falls Callback unsubscribed)
        if event_type in self._subscribers:
            for callback in list(self._subscribers[event_type]):
                self._call_callback(callback, event, "Event Handler Error")

        # Globale Subscriber benachrichtigen (Kopie, falls Callback unsubscribed)
        for callback in list(self._global_subscribers):
            self._call_callback(callback, event, "Global Event Handler Error")
        
        # Qt Signal emittieren
        self.event_emitted.emit(event)

    def _call_callback(self, callback: Callable, event: Event, error_label: str):
        """Ruft Subscriber direkt oder, für GUI-QObjects aus Worker-Threads, queued auf."""
        if self._should_queue_callback(callback):
            self._callback_requested.emit(callback, event)
            return

        try:
            callback(event)
        except Exception as e:
            print(f"{error_label}: {e}")

    def _should_queue_callback(self, callback: Callable) -> bool:
        receiver = getattr(callback, "__self__", None)
        if not isinstance(receiver, QObject):
            return False

        bus_thread = self.thread()
        return receiver.thread() == bus_thread and QThread.currentThread() != bus_thread

    def _dispatch_queued_callback(self, callback: Callable, event: Event):
        try:
            callback(event)
        except Exception as e:
            print(f"Queued Event Handler Error: {e}")
    
    def emit_file_opened(self, file_path: str, source: str = None):
        """Convenience: Datei geöffnet"""
        self.emit(EventType.FILE_OPENED, {'path': file_path}, source)
    
    def emit_file_saved(self, file_path: str, source: str = None):
        """Convenience: Datei gespeichert"""
        self.emit(EventType.FILE_SAVED, {'path': file_path}, source)
    
    def emit_status_message(self, message: str, timeout: int = 5000):
        """Convenience: Statusnachricht"""
        self.emit(EventType.STATUS_MESSAGE, {
            'message': message, 
            'timeout': timeout
        })
    
    def emit_errors(self, errors: List[Dict], file_path: str = None):
        """Convenience: Fehler gefunden"""
        self.emit(EventType.ERRORS_FOUND, {
            'errors': errors,
            'path': file_path
        })
    
    def emit_build_progress(self, progress: int, message: str = ""):
        """Convenience: Build-Fortschritt"""
        self.emit(EventType.BUILD_PROGRESS, {
            'progress': progress,
            'message': message
        })
    
    def get_history(self, event_type: EventType = None, 
                    limit: int = 10) -> List[Event]:
        """
        Gibt Event-History zurück
        
        Args:
            event_type: Optional - nur Events dieses Typs
            limit: Maximale Anzahl
            
        Returns:
            Liste der Events (neueste zuerst)
        """
        events = self._event_history[::-1]  # Umkehren
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[:limit]
    
    def clear_history(self):
        """Löscht die Event-History"""
        self._event_history.clear()


# Lazy Singleton - wird erst bei Aufruf erstellt (nach QApplication!)
_event_bus_instance = None

def get_event_bus() -> EventBus:
    """
    Gibt die globale EventBus-Instanz zurück.
    
    Lazy Initialization: Instanz wird erst beim ersten Aufruf erstellt,
    damit QApplication bereits existiert.
    """
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


if __name__ == "__main__":
    # Test
    bus = get_event_bus()
    
    def on_file_opened(event):
        print(f"File opened: {event.data}")
    
    bus.subscribe(EventType.FILE_OPENED, on_file_opened)
    bus.emit_file_opened("/test/file.py", "editor")
    
    print("History:", bus.get_history())
