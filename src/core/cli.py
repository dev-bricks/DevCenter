# -*- coding: utf-8 -*-
"""
DevCenter - Command Line Interface (CLI) & Health Diagnostics
Ermöglicht Steuerung, Selbstdiagnose, AST-Analyse, Headless-Build,
DB-sicheren Sync, Log-Einsicht und Workspace-Export über die Kommandozeile.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional

from core.app_paths import (
    get_app_data_dir,
    get_app_icon_path,
    get_log_file_path,
    get_logs_dir,
    get_settings_path,
)
from core.runtime_logging import get_logger, setup_logging

logger = get_logger("cli")

APP_VERSION = "1.0.3"


def build_parser() -> argparse.ArgumentParser:
    """Erstellt den Argument-Parser für die DevCenter CLI."""
    parser = argparse.ArgumentParser(
        prog="devcenter",
        description="DevCenter - Lokale Desktop-Entwicklungsumgebung für Python-Projekte",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Programmversion anzeigen und beenden",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ausführliche Debug-Ausgabe in Konsole und Logdatei aktivieren",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Explizites Log-Level festlegen (Standard: INFO, bzw. DEBUG bei --debug)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Systemdiagnose und Integritätsprüfung (Health-Check) durchführen",
    )
    parser.add_argument(
        "-s", "--status",
        action="store_true",
        help="Detaillierte Status- und Konfigurationsübersicht anzeigen",
    )
    parser.add_argument(
        "-l", "--logs",
        action="store_true",
        help="Einträge aus der Anwendungs-Logdatei anzeigen",
    )
    parser.add_argument(
        "--lines",
        type=int,
        default=50,
        metavar="N",
        help="Anzahl der anzuzeigenden Logzeilen bei --logs (Standard: 50)",
    )
    parser.add_argument(
        "--open",
        metavar="PATH",
        type=str,
        help="Projektordner direkt beim Start in DevCenter öffnen",
    )
    parser.add_argument(
        "--analyze",
        metavar="PATH",
        type=str,
        help="AST-Code-Analyse für eine Python-Datei oder ein Verzeichnis im Terminal ausführen",
    )
    parser.add_argument(
        "--export-workspace",
        metavar="PROJECT_PATH",
        type=str,
        help="Projekt-Workspace redigiert als JSON exportieren",
    )
    parser.add_argument(
        "--build",
        metavar="SCRIPT_PATH",
        type=str,
        help="Python-Skript mit PyInstaller zu EXE kompilieren (Headless-Build)",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        type=str,
        default="dist",
        help="Ausgabeverzeichnis für --build (Standard: dist)",
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        default=True,
        help="Ein-Datei-Binary erzeugen (Standard)",
    )
    parser.add_argument(
        "--onedir",
        action="store_false",
        dest="onefile",
        help="Verzeichnis-Bundle statt Ein-Datei-Binary erzeugen",
    )
    parser.add_argument(
        "--noconsole",
        action="store_true",
        default=False,
        help="Konsolenfenster für die kompilierte Binärdatei ausblenden",
    )
    parser.add_argument(
        "--icon",
        metavar="ICON_PATH",
        type=str,
        default=None,
        help="Icon-Datei (.ico) für den Kompilierungsvorgang",
    )
    parser.add_argument(
        "--sync",
        nargs=2,
        metavar=("SOURCE", "TARGET"),
        help="Dateien aus SOURCE nach TARGET synchronisieren (DB-sicherer Sync)",
    )
    parser.add_argument(
        "--backup",
        metavar="PROJECT_PATH",
        type=str,
        help="Projektordner sichern (erstellt Zeitstempel-Backup)",
    )
    parser.add_argument(
        "--backup-dir",
        metavar="DIR",
        type=str,
        default=None,
        help="Zielbasis-Verzeichnis für --backup (Standard: %APPDATA%/DevCenter/backups)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=str,
        help="Zieldatei für den Workspace-Export, Status- oder Analyse-Bericht",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ohne grafische Oberfläche (GUI) ausführen",
    )
    return parser


def run_health_check() -> int:
    """
    Führt eine strukturierte Systemdiagnose und Integritätsprüfung durch.
    Prüft Python-Version, PySide6, AST Analyzer, SQLite FTS5 und Pfade.

    Returns:
        int: 0 wenn alle Prüfungen bestanden wurden, sonst 1.
    """
    print("========================================")
    print("       DevCenter Systemdiagnose")
    print("========================================")
    all_passed = True
    results = []

    # 1. Python-Version
    py_ver = sys.version_info
    py_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    py_ok = py_ver >= (3, 10)
    results.append(("Python-Version (>= 3.10)", py_str, py_ok))
    if not py_ok:
        all_passed = False

    # 2. PySide6
    try:
        import PySide6
        pyside_ver = getattr(PySide6, "__version__", "OK")
        results.append(("PySide6 GUI-Framework", pyside_ver, True))
    except Exception as exc:
        results.append(("PySide6 GUI-Framework", f"Fehler: {exc}", False))
        all_passed = False

    # 3. MethodAnalyzer (AST)
    try:
        from modules.analyzer.method_analyzer import MethodAnalyzer
        analyzer = MethodAnalyzer()
        res = analyzer.analyze_code("def ping(): return 'pong'")
        ast_ok = len(res.functions) == 1
        results.append(("AST-Analyzer-Modul", "Verfügbar & funktional" if ast_ok else "Fehlerhaft", ast_ok))
        if not ast_ok:
            all_passed = False
    except Exception as exc:
        results.append(("AST-Analyzer-Modul", f"Fehler: {exc}", False))
        all_passed = False

    # 4. SQLite3 FTS5
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content);")
        conn.execute("INSERT INTO test_fts(content) VALUES('devcenter search');")
        cur = conn.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'devcenter';")
        match_ok = len(cur.fetchall()) == 1
        conn.close()
        results.append(("SQLite3 FTS5 Volltextindex", "Unterstützt", match_ok))
        if not match_ok:
            all_passed = False
    except Exception as exc:
        results.append(("SQLite3 FTS5 Volltextindex", f"Fehler: {exc}", False))
        all_passed = False

    # 5. Pfade & Verzeichnisse
    app_data = get_app_data_dir()
    logs_dir = get_logs_dir()
    settings_file = get_settings_path()
    paths_ok = True
    try:
        app_data.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        paths_ok = False
        all_passed = False
        logger.error("Fehler beim Erstellen der Verzeichnisse: %s", exc)

    results.append(("App-Konfigurationspfad", str(app_data), paths_ok))
    results.append(("App-Log-Verzeichnis", str(logs_dir), paths_ok))
    results.append(("Einstellungsdatei", str(settings_file), settings_file.exists()))

    # Ausgabe
    for label, val, ok in results:
        status_sym = "[OK]  " if ok else "[WARN]"
        print(f"{status_sym} {label:<30}: {val}")

    print("========================================")
    if all_passed:
        print("[Erfolg] Alle Integritätsprüfungen bestanden.")
        return 0
    else:
        print("[Warnung] Eine oder mehrere Prüfungen meldeten Fehler oder Warnungen.")
        return 1


def run_status(output_file: Optional[str] = None) -> int:
    """
    Gibt eine detaillierte Status- und Konfigurationsübersicht aus.
    Kann als formatierte Konsolenausgabe oder JSON-Datei exportiert werden.
    """
    from core.settings_manager import get_settings
    from core.project_manager import ProjectManager

    app_data = get_app_data_dir()
    settings_file = get_settings_path()
    logs_dir = get_logs_dir()
    log_file = get_log_file_path()
    icon_file = get_app_icon_path()

    settings = get_settings()

    # PyInstaller Check
    pyinstaller_ok = False
    pyinstaller_version = "nicht installiert"
    try:
        from modules.builder.kompilator import Kompilator
        komp = Kompilator()
        pyinstaller_ok = komp.check_pyinstaller()
        if pyinstaller_ok:
            pyinstaller_version = komp.get_pyinstaller_version()
    except Exception as exc:
        pyinstaller_version = f"Fehler: {exc}"

    # FTS5 Check
    fts5_supported = False
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content);")
        conn.close()
        fts5_supported = True
    except Exception:
        fts5_supported = False

    # Recent projects
    recent_projects: list[str] = []
    try:
        pm = ProjectManager()
        recent_projects = pm.get_recent_projects()
    except Exception as exc:
        logger.debug("Recent projects konnten nicht gelesen werden: %s", exc)

    status_data = {
        "app_name": "DevCenter",
        "version": APP_VERSION,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "language": getattr(settings, "language", "de"),
        "theme": getattr(getattr(settings, "appearance", None), "theme", "dark"),
        "paths": {
            "app_data_dir": str(app_data),
            "settings_path": str(settings_file),
            "settings_exists": settings_file.exists(),
            "logs_dir": str(logs_dir),
            "log_file": str(log_file),
            "log_exists": log_file.exists(),
            "log_size_bytes": log_file.stat().st_size if log_file.exists() else 0,
            "icon_path": str(icon_file),
            "icon_exists": icon_file.exists(),
        },
        "capabilities": {
            "pyinstaller_available": pyinstaller_ok,
            "pyinstaller_version": pyinstaller_version,
            "sqlite_fts5": fts5_supported,
        },
        "recent_projects": recent_projects,
    }

    if output_file:
        out_p = Path(output_file).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        print(f"[Erfolg] Status-Bericht gespeichert unter: {out_p}")
        return 0

    print("========================================")
    print(f"       DevCenter Status (v{APP_VERSION})")
    print("========================================")
    print(f"Version:              {status_data['version']}")
    print(f"Python:               {status_data['python_version']} ({status_data['platform']})")
    print(f"Sprache / Theme:      {status_data['language']} / {status_data['theme']}")
    print("--- Pfade & Speicherorte ---")
    print(f"Konfigurationsordner: {status_data['paths']['app_data_dir']}")
    print(f"Einstellungen:        {status_data['paths']['settings_path']} ({'vorhanden' if status_data['paths']['settings_exists'] else 'fehlt'})")
    print(f"Logdatei:             {status_data['paths']['log_file']} ({status_data['paths']['log_size_bytes']} Bytes)")
    print(f"Anwendungs-Icon:      {status_data['paths']['icon_path']} ({'vorhanden' if status_data['paths']['icon_exists'] else 'fehlt'})")
    print("--- Module & Fähigkeiten ---")
    print(f"PyInstaller:          {pyinstaller_version} ({'aktiv' if pyinstaller_ok else 'fehlt'})")
    print(f"SQLite FTS5 Index:    {'unterstützt' if fts5_supported else 'nicht verfügbar'}")
    print("--- Zuletzt geöffnete Projekte ---")
    if recent_projects:
        for p in recent_projects[:5]:
            print(f"  • {p}")
        if len(recent_projects) > 5:
            print(f"  ... und {len(recent_projects) - 5} weitere")
    else:
        print("  (keine kürzlichen Projekte verzeichnet)")
    print("========================================")
    return 0


def run_show_logs(lines_count: int = 50) -> int:
    """
    Zeigt die letzten N Logzeilen der Anwendungs-Logdatei an.
    """
    log_file = get_log_file_path()
    if not log_file.exists():
        print(f"[Info] Keine Logdatei vorhanden unter: {log_file}")
        return 0

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()

        count = max(1, lines_count)
        tail_lines = all_lines[-count:] if len(all_lines) > count else all_lines

        print(f"--- DevCenter Logs ({log_file}) [Zeilen: {len(tail_lines)}/{len(all_lines)}] ---")
        for line in tail_lines:
            print(line, end="")
        if tail_lines and not tail_lines[-1].endswith("\n"):
            print()
        return 0
    except Exception as exc:
        print(f"[Fehler] Logdatei konnte nicht gelesen werden: {exc}", file=sys.stderr)
        return 1


def run_build(
    script_path_str: str,
    output_dir: str = "dist",
    one_file: bool = True,
    console: bool = True,
    icon: Optional[str] = None,
) -> int:
    """
    Führt einen Headless-Build mit PyInstaller über den Kompilator durch.
    """
    from modules.builder.kompilator import BuildConfig, Kompilator

    script_path = Path(script_path_str).resolve()
    if not script_path.is_file():
        print(f"[Fehler] Build-Skript nicht gefunden: {script_path}", file=sys.stderr)
        return 1

    komp = Kompilator()
    if not komp.check_pyinstaller():
        print("[Fehler] PyInstaller ist in dieser Umgebung nicht installiert.", file=sys.stderr)
        return 1

    config = BuildConfig(
        script_path=str(script_path),
        output_dir=output_dir,
        one_file=one_file,
        console=console,
        icon=icon,
    )

    def on_progress(percent: int, message: str) -> None:
        print(f"[{percent:3d}%] {message}")

    komp.set_progress_callback(on_progress)
    print(f"[Build] Starte Kompilierung für {script_path.name}...")
    result = komp.build(config)

    if result.success:
        print(f"[Erfolg] Build abgeschlossen in {result.duration:.2f}s!")
        if result.output_path:
            print(f"Artefakt: {result.output_path}")
        return 0
    else:
        print(f"[Fehler] Build fehlgeschlagen: {result.error_message}", file=sys.stderr)
        return 1


def run_sync(source_str: str, target_str: str) -> int:
    """
    Führt eine dateisystem- und DB-sichere Synchronisation durch.
    """
    from modules.filemanager.sync_manager import SyncConfig, SyncManager

    src = Path(source_str).resolve()
    dst = Path(target_str).resolve()

    if not src.is_dir():
        print(f"[Fehler] Quellverzeichnis existiert nicht: {src}", file=sys.stderr)
        return 1

    def on_progress(percent: int, message: str) -> None:
        print(f"[{percent:3d}%] {message}")

    manager = SyncManager()
    manager.set_progress_callback(on_progress)
    config = SyncConfig(source_path=str(src), target_path=str(dst))

    print(f"[Sync] Synchronisiere von '{src}' nach '{dst}'...")
    res = manager.sync(config)

    if res.success:
        print(
            f"[Erfolg] Sync abgeschlossen in {res.duration:.2f}s! "
            f"Kopiert: {res.files_copied}, Übersprungen: {res.files_skipped}, "
            f"Bytes: {res.bytes_copied}"
        )
        return 0
    else:
        print(f"[Fehler] Sync mit Fehlern beendet: {res.errors}", file=sys.stderr)
        return 1


def run_backup(project_path_str: str, backup_base_dir: Optional[str] = None) -> int:
    """
    Erstellt ein Backup eines Projektordners.
    """
    from modules.filemanager.sync_manager import SyncManager

    proj_dir = Path(project_path_str).resolve()
    if not proj_dir.is_dir():
        print(f"[Fehler] Projektordner nicht gefunden: {proj_dir}", file=sys.stderr)
        return 1

    if not backup_base_dir:
        backup_base = get_app_data_dir() / "backups"
    else:
        backup_base = Path(backup_base_dir).resolve()

    backup_base.mkdir(parents=True, exist_ok=True)

    manager = SyncManager()

    def on_progress(percent: int, message: str) -> None:
        print(f"[{percent:3d}%] {message}")

    manager.set_progress_callback(on_progress)
    print(f"[Backup] Sichere Projekt '{proj_dir.name}' nach '{backup_base}'...")
    res = manager.backup_project(str(proj_dir), str(backup_base))

    if res.success:
        print(
            f"[Erfolg] Backup erfolgreich erstellt in {res.duration:.2f}s! "
            f"Dateien gesichert: {res.files_copied}, Bytes: {res.bytes_copied}"
        )
        return 0
    else:
        print(f"[Fehler] Backup fehlgeschlagen: {res.errors}", file=sys.stderr)
        return 1


def run_ast_analysis(target_path_str: str, output_file: Optional[str] = None) -> int:
    """
    Führt eine statische AST-Code-Analyse für eine Datei oder einen Ordner durch.
    Kann als formatierte Konsolenausgabe oder JSON-Datei exportiert werden.
    """
    from modules.analyzer.method_analyzer import MethodAnalyzer

    target = Path(target_path_str).resolve()
    if not target.exists():
        print(f"[Fehler] Pfad nicht gefunden: {target}", file=sys.stderr)
        return 1

    analyzer = MethodAnalyzer()
    py_files = [target] if target.is_file() else list(target.rglob("*.py"))

    if not py_files:
        print(f"[Info] Keine Python-Dateien (.py) gefunden unter: {target}")
        return 0

    total_classes = 0
    total_methods = 0
    total_lines = 0
    total_issues = 0
    details = []

    for fpath in py_files:
        try:
            res = analyzer.analyze_file(str(fpath))
            methods_in_classes = sum(len(c.methods) for c in res.classes)
            func_count = len(res.functions) + methods_in_classes
            issues_count = len(res.errors) + len(res.warnings)
            total_classes += len(res.classes)
            total_methods += func_count
            total_lines += res.total_lines
            total_issues += issues_count
            details.append({
                "file": str(fpath),
                "classes": len(res.classes),
                "methods": func_count,
                "lines": res.total_lines,
                "issues": issues_count,
            })
        except Exception as exc:
            logger.warning("Fehler bei Analyse von %s: %s", fpath, exc)

    summary = {
        "target": str(target),
        "files_analyzed": len(py_files),
        "total_classes": total_classes,
        "total_methods": total_methods,
        "total_lines": total_lines,
        "total_issues": total_issues,
        "files": details,
    }

    if output_file:
        out_p = Path(output_file).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[Erfolg] Analyse-Bericht gespeichert unter: {out_p}")
    else:
        print("\n--- Analyse-Zusammenfassung ---")
        print(f"Dateien analysiert:    {len(py_files)}")
        print(f"Klassen gefunden:      {total_classes}")
        print(f"Methoden gefunden:     {total_methods}")
        print(f"Codezeilen (gesamt):   {total_lines}")
        print(f"Gefundene Probleme:    {total_issues}")

    return 0


def run_workspace_export(project_path_str: str, output_file: Optional[str] = None) -> int:
    """
    Exportiert das Projekt als redigierten devcenter-workspace-v1.json Workspace.
    """
    from core.workspace_export import export_workspace
    from core.project_manager import ProjectManager, ProjectConfig
    from core.settings_manager import get_settings

    proj_dir = Path(project_path_str).resolve()
    if not proj_dir.is_dir():
        print(f"[Fehler] Projektverzeichnis nicht gefunden: {proj_dir}", file=sys.stderr)
        return 1

    try:
        from datetime import datetime
        pm = ProjectManager()
        project = pm.open_project(str(proj_dir))
        if not project:
            # Projekt besitzt noch keine devcenter.json -> temporäre Konfiguration für Export ableiten
            main_file = None
            if (proj_dir / "main.py").exists():
                main_file = "main.py"
            elif (proj_dir / "src" / "main.py").exists():
                main_file = "src/main.py"

            now_iso = datetime.now().isoformat()
            project = ProjectConfig(
                name=proj_dir.name or "Projekt",
                path=str(proj_dir),
                created=now_iso,
                last_opened=now_iso,
                main_file=main_file,
            )

        settings = get_settings()
        out_path = Path(output_file).resolve() if output_file else (proj_dir / "devcenter-workspace-v1.json")
        export_workspace(project, settings, str(out_path))
        print(f"[Erfolg] Workspace erfolgreich exportiert nach: {out_path}")
        return 0
    except Exception as exc:
        print(f"[Fehler] Workspace-Export fehlgeschlagen: {exc}", file=sys.stderr)
        return 1


def run_cli(argv: Optional[list[str]] = None) -> int | argparse.Namespace:
    """
    Parst CLI-Argumente, richtet Logging ein und dispatcht Befehle.

    Returns:
        int: Exit-Code, wenn ein CLI-Befehl (--version, --check, --analyze, etc.) ausgeführt wurde.
        argparse.Namespace: Wenn die GUI mit den Parametern gestartet werden soll.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Logging konfigurieren
    log_level = "DEBUG" if args.debug else (args.log_level or "INFO")
    setup_logging(level=log_level)

    logger.debug("DevCenter gestartet mit Argumenten: %s", args)

    # 1. Version
    if args.version:
        print(f"DevCenter {APP_VERSION}")
        return 0

    # 2. Health-Check
    if args.check:
        return run_health_check()

    # 3. Status
    if args.status:
        return run_status(output_file=args.output)

    # 4. Logs
    if args.logs:
        return run_show_logs(lines_count=args.lines)

    # 5. AST-Analyse
    if args.analyze:
        return run_ast_analysis(args.analyze, output_file=args.output)

    # 6. Workspace-Export
    if args.export_workspace:
        return run_workspace_export(args.export_workspace, output_file=args.output)

    # 7. Headless-Build
    if args.build:
        return run_build(
            script_path_str=args.build,
            output_dir=args.output_dir,
            one_file=args.onefile,
            console=not args.noconsole,
            icon=args.icon,
        )

    # 8. Sync
    if args.sync:
        return run_sync(source_str=args.sync[0], target_str=args.sync[1])

    # 9. Backup
    if args.backup:
        return run_backup(project_path_str=args.backup, backup_base_dir=args.backup_dir)

    # 10. Headless ohne spezifische Aktion
    if args.headless:
        if args.open:
            print(f"[Headless] Projektpfad verifiziert: {args.open}")
            return 0
        parser.print_help()
        return 0

    # GUI starten
    return args
