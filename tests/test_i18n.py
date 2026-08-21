# -*- coding: utf-8 -*-
"""
DevCenter - I18N Unit Tests
Testet das TranslationSystem, die 6-Sprachen-Parität (DE, EN, ES, ZH, JA, RU)
und die Fallback-Kette gemäß Policy P-006.
"""

import json
import unittest
from pathlib import Path

from translator import (
    TranslationSystem,
    detect_system_language,
    SUPPORTED_LANGUAGES,
    LANGUAGE_NAMES,
    DEFAULT_LANGUAGE
)


class TestDevCenterI18N(unittest.TestCase):
    """Testsuite für DevCenter Translation System und Mehrsprachigkeit."""

    def setUp(self):
        self.app_dir = Path(__file__).parent.parent
        self.locales_dir = self.app_dir / "locales"
        self.ts_de = TranslationSystem(default_lang="de", app_dir=self.app_dir)
        self.ts_en = TranslationSystem(default_lang="en", app_dir=self.app_dir)
        self.ts_es = TranslationSystem(default_lang="es", app_dir=self.app_dir)
        self.ts_zh = TranslationSystem(default_lang="zh", app_dir=self.app_dir)
        self.ts_ja = TranslationSystem(default_lang="ja", app_dir=self.app_dir)
        self.ts_ru = TranslationSystem(default_lang="ru", app_dir=self.app_dir)

    def test_translations_json_exists_and_valid_6_languages(self):
        """Prüft, ob translations.json existiert und alle 6 Sprachen lückenlos befüllt sind."""
        json_path = self.locales_dir / "translations.json"
        self.assertTrue(json_path.exists(), "translations.json muss existieren")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertGreater(len(data), 50, "Mindestens 50 Translation-Keys erwartet")

        for key, entry in data.items():
            for lang in SUPPORTED_LANGUAGES:
                self.assertIn(lang, entry, f"Sprachcode '{lang}' fehlt im Key '{key}'")
                val = entry[lang]
                self.assertTrue(bool(val and val.strip()), f"Sprachcode '{lang}' ist leer für Key '{key}'")

    def test_supported_languages_and_names(self):
        """Prüft, ob alle 6 Sprachen in den Konstanten registriert sind."""
        self.assertEqual(DEFAULT_LANGUAGE, "de")
        self.assertEqual(len(SUPPORTED_LANGUAGES), 6)
        self.assertIn("de", SUPPORTED_LANGUAGES)
        self.assertIn("en", SUPPORTED_LANGUAGES)
        self.assertIn("es", SUPPORTED_LANGUAGES)
        self.assertIn("zh", SUPPORTED_LANGUAGES)
        self.assertIn("ja", SUPPORTED_LANGUAGES)
        self.assertIn("ru", SUPPORTED_LANGUAGES)

        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(lang, LANGUAGE_NAMES)
            self.assertTrue(len(LANGUAGE_NAMES[lang]) > 0)

    def test_translation_all_6_languages(self):
        """Prüft konkrete Übersetzungen über alle 6 Sprachen."""
        # Menü & Dialog Keys
        self.assertEqual(self.ts_de.t("&Analyse"), "&Analyse")
        self.assertEqual(self.ts_en.t("&Analyse"), "&Analysis")
        self.assertEqual(self.ts_es.t("&Analyse"), "&Análisis")
        self.assertEqual(self.ts_zh.t("&Analyse"), "&分析")
        self.assertEqual(self.ts_ja.t("&Analyse"), "&分析")
        self.assertEqual(self.ts_ru.t("&Analyse"), "&Анализ")

        self.assertEqual(self.ts_de.t("Einstellungen"), "Einstellungen")
        self.assertEqual(self.ts_en.t("Einstellungen"), "Settings")
        self.assertEqual(self.ts_es.t("Einstellungen"), "Ajustes")
        self.assertEqual(self.ts_zh.t("Einstellungen"), "设置")
        self.assertEqual(self.ts_ja.t("Einstellungen"), "設定")
        self.assertEqual(self.ts_ru.t("Einstellungen"), "Настройки")

        self.assertEqual(self.ts_de.t("Build-Einstellungen"), "Build-Einstellungen")
        self.assertEqual(self.ts_en.t("Build-Einstellungen"), "Build Settings")
        self.assertEqual(self.ts_es.t("Build-Einstellungen"), "Ajustes de compilación")
        self.assertEqual(self.ts_zh.t("Build-Einstellungen"), "构建设置")
        self.assertEqual(self.ts_ja.t("Build-Einstellungen"), "ビルド設定")
        self.assertEqual(self.ts_ru.t("Build-Einstellungen"), "Настройки сборки")

        self.assertEqual(self.ts_de.t("Abbrechen"), "Abbrechen")
        self.assertEqual(self.ts_en.t("Abbrechen"), "Cancel")
        self.assertEqual(self.ts_es.t("Abbrechen"), "Cancelar")
        self.assertEqual(self.ts_zh.t("Abbrechen"), "取消")
        self.assertEqual(self.ts_ja.t("Abbrechen"), "キャンセル")
        self.assertEqual(self.ts_ru.t("Abbrechen"), "Отмена")

        self.assertEqual(self.ts_de.t("Neues Projekt erstellen"), "Neues Projekt erstellen")
        self.assertEqual(self.ts_en.t("Neues Projekt erstellen"), "Create New Project")
        self.assertEqual(self.ts_es.t("Neues Projekt erstellen"), "Crear nuevo proyecto")
        self.assertEqual(self.ts_zh.t("Neues Projekt erstellen"), "创建新项目")
        self.assertEqual(self.ts_ja.t("Neues Projekt erstellen"), "新規プロジェクトを作成")
        self.assertEqual(self.ts_ru.t("Neues Projekt erstellen"), "Создать новый проект")

    def test_fallback_for_unknown_key(self):
        """Unbekannte Keys werden als Fallback unverändert zurückgegeben."""
        unknown = "UnbekannterKey123456789"
        self.assertEqual(self.ts_de.t(unknown), unknown)
        self.assertEqual(self.ts_en.t(unknown), unknown)
        self.assertEqual(self.ts_es.t(unknown), unknown)
        self.assertEqual(self.ts_zh.t(unknown), unknown)
        self.assertEqual(self.ts_ja.t(unknown), unknown)
        self.assertEqual(self.ts_ru.t(unknown), unknown)

    def test_fallback_chain_tier_resolution(self):
        """Prüft die 4-stufige Fallback-Kette: lang -> en -> de -> key."""
        ts = TranslationSystem(default_lang="es", app_dir=self.app_dir)

        # 1. Fall: es fehlt, en vorhanden -> nutzt en
        ts.translations["MockKey1"] = {"de": "Deutscher Text", "en": "English Fallback", "es": ""}
        self.assertEqual(ts.t("MockKey1"), "English Fallback")

        # 2. Fall: es und en fehlen, de vorhanden -> nutzt de
        ts.translations["MockKey2"] = {"de": "Deutscher Fallback", "en": "", "es": ""}
        self.assertEqual(ts.t("MockKey2"), "Deutscher Fallback")

    def test_language_switching(self):
        """Prüft dynamisches Umschalten der UI-Sprache."""
        ts = TranslationSystem(default_lang="de", app_dir=self.app_dir)
        self.assertEqual(ts.get_language(), "de")
        self.assertEqual(ts.t("Speichern"), "Speichern")

        ts.set_language("en")
        self.assertEqual(ts.get_language(), "en")
        self.assertEqual(ts.t("Speichern"), "Save")

        ts.set_language("es")
        self.assertEqual(ts.get_language(), "es")
        self.assertEqual(ts.t("Speichern"), "Guardar")

        ts.set_language("zh")
        self.assertEqual(ts.get_language(), "zh")
        self.assertEqual(ts.t("Speichern"), "保存")

        ts.set_language("ja")
        self.assertEqual(ts.get_language(), "ja")
        self.assertEqual(ts.t("Speichern"), "保存")

        ts.set_language("ru")
        self.assertEqual(ts.get_language(), "ru")
        self.assertEqual(ts.t("Speichern"), "Сохранить")

        # Ungültige Sprache wird ignoriert
        ts.set_language("invalid_lang_code")
        self.assertEqual(ts.get_language(), "ru")

    def test_no_missing_translations_across_all_languages(self):
        """Stellt sicher, dass keine Sprache fehlende Übersetzungsschlüssel hat."""
        for lang in SUPPORTED_LANGUAGES:
            missing = self.ts_de.get_missing_translations(lang)
            self.assertEqual(missing, [], f"Sprache '{lang}' hat unvollständige Übersetzungen: {missing}")

    def test_detect_system_language(self):
        """Prüft, ob die Systemsprachenerkennung einen gültigen Sprachcode liefert."""
        lang = detect_system_language()
        self.assertIn(lang, SUPPORTED_LANGUAGES)


if __name__ == "__main__":
    unittest.main()
