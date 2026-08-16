# -*- coding: utf-8 -*-
"""
DevCenter - Settings Manager
Zentrale Einstellungsverwaltung
"""

import json
import keyring
from keyring.errors import NoKeyringError, PasswordDeleteError
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field, fields
from PySide6.QtCore import QByteArray, QObject, Signal

from core.app_paths import get_settings_path


KEYRING_SERVICE = "DevCenter"
KEYRING_ACCOUNT = "anthropic_api_key"


@dataclass
class EditorSettings:
    """Editor-Einstellungen"""
    font_family: str = "Consolas"
    font_size: int = 11
    tab_size: int = 4
    use_spaces: bool = True
    show_line_numbers: bool = True
    show_whitespace: bool = False
    word_wrap: bool = False
    auto_indent: bool = True
    highlight_current_line: bool = True
    auto_complete: bool = True
    auto_save: bool = False
    auto_save_interval: int = 60  # Sekunden


@dataclass
class BuildSettings:
    """Build-Einstellungen"""
    pyinstaller_path: str = ""
    default_output_dir: str = "dist"
    one_file: bool = True
    console_mode: bool = True
    upx_enabled: bool = False
    upx_path: str = ""
    clean_build: bool = True
    include_licenses: bool = True


@dataclass
class AISettings:
    """AI-Einstellungen"""
    api_key: str = ""  # Nur im Speicher; persistent ausschließlich im System-Keyring
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True


@dataclass
class SyncSettings:
    """Sync-Einstellungen"""
    enabled: bool = False
    backup_path: str = ""
    auto_backup: bool = False
    backup_interval: int = 300  # Sekunden
    excludes: list = field(default_factory=lambda: [
        "__pycache__", ".git", "dist", "build", "*.pyc", "*.pyo"
    ])


@dataclass
class AppearanceSettings:
    """Erscheinungsbild-Einstellungen"""
    theme: str = "dark"  # dark, light, system
    accent_color: str = "#3498db"
    editor_theme: str = "monokai"
    show_toolbar: bool = True
    show_statusbar: bool = True
    compact_mode: bool = False


@dataclass
class GeneralSettings:
    """Allgemeine Anwendungseinstellungen"""
    open_last_project: bool = False


@dataclass
class AppSettings:
    """Gesamte Anwendungseinstellungen"""
    editor: EditorSettings = field(default_factory=EditorSettings)
    build: BuildSettings = field(default_factory=BuildSettings)
    ai: AISettings = field(default_factory=AISettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    general: GeneralSettings = field(default_factory=GeneralSettings)

    # Allgemeine Einstellungen
    language: str = "de"
    check_updates: bool = True
    telemetry_enabled: bool = False
    window_state: Dict[str, Any] = field(default_factory=dict)


class SettingsManager(QObject):
    """
    Zentrale Einstellungsverwaltung für DevCenter

    Signals:
        settings_changed: Eine Einstellung hat sich geändert (key, value)
        theme_changed: Theme wurde geändert (theme_name)
    """

    settings_changed = Signal(str, object)
    theme_changed = Signal(str)

    def __init__(self, settings_path: str = None):
        super().__init__()
        self.settings_path = settings_path or self._default_settings_path()
        self.settings = AppSettings()
        self._extra_settings: Dict[str, Any] = {}
        self._load()

    def _default_settings_path(self) -> str:
        """Standardpfad für Einstellungen"""
        settings_dir = get_settings_path().parent
        settings_dir.mkdir(parents=True, exist_ok=True)
        return str(settings_dir / 'settings.json')

    def _load(self):
        """Lädt Einstellungen aus Datei"""
        settings_file = Path(self.settings_path)

        if not settings_file.exists():
            self.settings.ai.api_key = self._read_api_key()
            self._save()  # Standardeinstellungen speichern
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            raw_ai = data.get('ai')
            legacy_api_key = ""
            if isinstance(raw_ai, dict):
                legacy_api_key = str(raw_ai.get('api_key') or "")

            # Einstellungen rekonstruieren
            self._extra_settings = self._extract_extra_settings(data)
            if 'editor' in data:
                self.settings.editor = self._load_section(data['editor'], EditorSettings)
            if 'build' in data:
                self.settings.build = self._load_section(data['build'], BuildSettings)
            if 'ai' in data:
                self.settings.ai = self._load_section(data['ai'], AISettings)
            if 'sync' in data:
                self.settings.sync = self._load_section(data['sync'], SyncSettings)
            if 'appearance' in data:
                self.settings.appearance = self._load_section(data['appearance'], AppearanceSettings)
            if 'general' in data:
                self.settings.general = self._load_section(data['general'], GeneralSettings)

            # Allgemeine Einstellungen
            self.settings.language = data.get('language', 'de')
            self.settings.check_updates = data.get('check_updates', True)
            self.settings.telemetry_enabled = data.get('telemetry_enabled', False)
            self.settings.window_state = data.get('window_state', {})

            stored_api_key = self._read_api_key()
            legacy_cleanup_succeeded = True
            if isinstance(raw_ai, dict) and 'api_key' in raw_ai:
                legacy_cleanup_succeeded = self._save()
                if not legacy_cleanup_succeeded:
                    print(
                        "Sicherheitswarnung: Legacy-API-Key konnte nicht aus "
                        "settings.json entfernt werden."
                    )

            if stored_api_key:
                self.settings.ai.api_key = stored_api_key
            elif legacy_api_key:
                if not legacy_cleanup_succeeded or not self._store_api_key(legacy_api_key):
                    # Die Datei wird zuerst bereinigt. Schlägt das fehl, entsteht
                    # keine zusätzliche persistente Kopie im Keyring.
                    self.settings.ai.api_key = legacy_api_key

        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
            self.settings = AppSettings()
            self._extra_settings = {}

    def _load_section(self, raw: Any, settings_type):
        """Build a settings dataclass from known fields and ignore extra keys."""
        if not isinstance(raw, dict):
            return settings_type()
        valid_fields = {item.name for item in fields(settings_type)}
        values = {key: value for key, value in raw.items() if key in valid_fields}
        return settings_type(**values)

    def _extract_extra_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Keep unknown persisted settings so older UI aliases are not lost."""
        known_top_level = {
            'editor',
            'build',
            'ai',
            'sync',
            'appearance',
            'general',
            'language',
            'check_updates',
            'telemetry_enabled',
            'window_state',
        }
        section_types = {
            'editor': EditorSettings,
            'build': BuildSettings,
            'ai': AISettings,
            'sync': SyncSettings,
            'appearance': AppearanceSettings,
            'general': GeneralSettings,
        }
        extra: Dict[str, Any] = {
            key: value for key, value in data.items() if key not in known_top_level
        }
        for section, settings_type in section_types.items():
            raw = data.get(section)
            if not isinstance(raw, dict):
                continue
            valid_fields = {item.name for item in fields(settings_type)}
            section_extra = {
                key: value for key, value in raw.items() if key not in valid_fields
            }
            if section_extra:
                extra[section] = section_extra
        return extra

    def _save(self) -> bool:
        """Speichert Einstellungen in Datei"""
        settings_file = Path(self.settings_path)
        settings_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = self._settings_to_dict()

            # recent_projects wird von ProjectManager verwaltet — nie mit veralteter Kopie überschreiben
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        current_data = json.load(f)
                    if 'recent_projects' in current_data:
                        data['recent_projects'] = current_data['recent_projects']
                except (json.JSONDecodeError, OSError):
                    pass

            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True

        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
            return False

    def _settings_to_dict(self) -> Dict[str, Any]:
        """Serialize known settings plus custom settings."""
        ai_settings = asdict(self.settings.ai)
        ai_settings.pop('api_key', None)
        known = {
                'editor': asdict(self.settings.editor),
                'build': asdict(self.settings.build),
                'ai': ai_settings,
                'sync': asdict(self.settings.sync),
                'appearance': asdict(self.settings.appearance),
                'general': asdict(self.settings.general),
                'language': self.settings.language,
                'check_updates': self.settings.check_updates,
                'telemetry_enabled': self.settings.telemetry_enabled,
                'window_state': self.settings.window_state
            }
        data = deepcopy(self._extra_settings)
        self._deep_update(data, known)
        if isinstance(data.get('ai'), dict):
            data['ai'].pop('api_key', None)
        return data

    def _read_api_key(self) -> str:
        """Liest den Anthropic-Key ausschließlich aus dem System-Keyring."""
        try:
            return keyring.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT) or ""
        except Exception as exc:
            print(f"System-Keyring nicht verfügbar: {exc}")
            return ""

    def _store_api_key(self, api_key: str) -> bool:
        """Speichert oder entfernt den Anthropic-Key im System-Keyring."""
        try:
            if api_key:
                keyring.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, api_key)
            else:
                try:
                    keyring.delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
                except PasswordDeleteError:
                    pass
            self.settings.ai.api_key = api_key
            return True
        except NoKeyringError:
            # Kein Keyring-Backend auf diesem System installiert (z. B. headless
            # CI-Runner ohne Secret-Service). Ohne Backend gibt es nichts zu
            # persistieren oder zu leaken — im Gegensatz zu einem vorhandenen,
            # aber fehlschlagenden Backend darf das reset_to_defaults()/set()
            # nicht blockieren.
            self.settings.ai.api_key = api_key
            return True
        except Exception as exc:
            print(f"API-Key konnte nicht im System-Keyring gespeichert werden: {exc}")
            return False

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Merge source into target while keeping nested extra keys."""
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def _get_from(self, source: Any, key: str, missing: object) -> Any:
        obj = source
        for part in key.split('.'):
            if isinstance(obj, dict):
                if part not in obj:
                    return missing
                obj = obj[part]
            elif hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return missing
        return obj

    def _set_known(self, key: str, value: Any) -> bool:
        parts = key.split('.')
        obj = self.settings
        for part in parts[:-1]:
            if isinstance(obj, dict):
                child = obj.setdefault(part, {})
                if not isinstance(child, dict):
                    return False
                obj = child
            elif hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return False

        final_key = parts[-1]
        if isinstance(obj, dict):
            obj[final_key] = value
            return True
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            return True
        return False

    def _set_extra(self, key: str, value: Any) -> None:
        parts = key.split('.')
        obj = self._extra_settings
        for part in parts[:-1]:
            child = obj.setdefault(part, {})
            if not isinstance(child, dict):
                child = {}
                obj[part] = child
            obj = child
        obj[parts[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Einstellungswert

        Args:
            key: Punktnotation z.B. "editor.font_size"
            default: Standardwert wenn nicht gefunden

        Returns:
            Einstellungswert oder default
        """
        missing = object()
        try:
            value = self._get_from(self.settings, key, missing)
            if value is not missing:
                return value
            value = self._get_from(self._extra_settings, key, missing)
            return default if value is missing else value
        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Setzt einen Einstellungswert

        Args:
            key: Punktnotation z.B. "editor.font_size"
            value: Neuer Wert
            save: Sofort speichern
        """
        try:
            if key == 'ai.api_key':
                if not self._store_api_key(str(value or "")):
                    return False
                self.settings_changed.emit(key, value)
                return True

            if not self._set_known(key, value):
                self._set_extra(key, value)

            if save:
                if not self._save():
                    return False

            self.settings_changed.emit(key, value)

            # Spezielle Signale
            if key.startswith('appearance.theme'):
                self.theme_changed.emit(value)
            return True

        except Exception as e:
            print(f"Fehler beim Setzen von {key}: {e}")
            return False

    def reset_to_defaults(self, category: str = None) -> bool:
        """
        Setzt Einstellungen auf Standard zurück

        Args:
            category: Optional - nur diese Kategorie zurücksetzen
        """
        if category is None:
            if not self._store_api_key(""):
                return False
            self.settings = AppSettings()
        elif category == 'editor':
            self.settings.editor = EditorSettings()
        elif category == 'build':
            self.settings.build = BuildSettings()
        elif category == 'ai':
            if not self._store_api_key(""):
                return False
            self.settings.ai = AISettings()
        elif category == 'sync':
            self.settings.sync = SyncSettings()
        elif category == 'appearance':
            self.settings.appearance = AppearanceSettings()
        elif category == 'general':
            self.settings.general = GeneralSettings()

        if not self._save():
            return False
        self.settings_changed.emit('*', None)
        return True

    def export_settings(self, path: str) -> bool:
        """Exportiert Einstellungen in eine Datei"""
        try:
            data = self._settings_to_dict()

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False

    def import_settings(self, path: str) -> bool:
        """Importiert Einstellungen aus einer Datei"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Einstellungen übernehmen
            self._extra_settings = self._extract_extra_settings(data)
            if 'editor' in data:
                self.settings.editor = self._load_section(data['editor'], EditorSettings)
            if 'build' in data:
                self.settings.build = self._load_section(data['build'], BuildSettings)
            current_api_key = self.settings.ai.api_key
            if 'ai' in data:
                self.settings.ai = self._load_section(data['ai'], AISettings)
                self.settings.ai.api_key = current_api_key
            if 'sync' in data:
                self.settings.sync = self._load_section(data['sync'], SyncSettings)
            if 'appearance' in data:
                self.settings.appearance = self._load_section(data['appearance'], AppearanceSettings)
            if 'general' in data:
                self.settings.general = self._load_section(data['general'], GeneralSettings)

            if not self._save():
                return False
            self.settings_changed.emit('*', None)
            return True
        except Exception as e:
            print(f"Import-Fehler: {e}")
            return False

    def save_window_state(self, geometry: bytes, state: bytes):
        """Speichert Fensterzustand"""
        self.settings.window_state = {
            'geometry': self._serialize_qt_bytes(geometry),
            'state': self._serialize_qt_bytes(state),
        }
        self._save()

    def restore_window_state(self) -> tuple:
        """Stellt Fensterzustand wieder her"""
        ws = self.settings.window_state
        geometry = self._deserialize_qt_bytes(ws.get('geometry', ''))
        state = self._deserialize_qt_bytes(ws.get('state', ''))
        return geometry, state

    def _serialize_qt_bytes(self, value: Any) -> str:
        """Serialize Qt byte containers and plain bytes as hex strings."""
        if not value:
            return ''
        if isinstance(value, QByteArray):
            raw = bytes(value)
        elif isinstance(value, (bytes, bytearray)):
            raw = bytes(value)
        else:
            raw = bytes(value)
        return raw.hex()

    def _deserialize_qt_bytes(self, value: str) -> Optional[QByteArray]:
        """Restore serialized window state into a QByteArray for Qt APIs."""
        if not value:
            return None
        return QByteArray.fromHex(value.encode('ascii'))


# Singleton-Instance
_instance: Optional[SettingsManager] = None

def get_settings() -> SettingsManager:
    """Gibt die globale Settings-Instanz zurück"""
    global _instance
    if _instance is None:
        _instance = SettingsManager()
    return _instance


if __name__ == "__main__":
    # Test
    sm = SettingsManager()
    print(f"Font Size: {sm.get('editor.font_size')}")
    print(f"Theme: {sm.get('appearance.theme')}")
