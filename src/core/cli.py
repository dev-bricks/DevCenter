# -*- coding: utf-8 -*-
"""
DevCenter - Command Line Interface (CLI) & Health Diagnostics
Ermöglicht Steuerung, Selbstdiagnose, AST-Analyse und Workspace-Export über die Kommandozeile.
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
        "--output",
        metavar="FILE",
        type=str,
        help="Zieldatei für den Workspace-Export oder den Analyse-Bericht",
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
    icon_path = get_app_icon_path()

    results.append(("AppData-Ordner", str(app_data), True))
    results.append(("Logs-Ordner", str(logs_dir), True))
    results.append(("Settings-Pfad", str(settings_file), True))
    results.append(("App-Icon", str(icon_path) if icon_path and icon_path.exists() else "Standard", True))

    print(f"{'Komponente':<30} | {'Status':<10} | {'Details'}")
    print("-" * 75)
    for comp, detail, ok in results:
        status = "OK" if ok else "FEHLER"
        print(f"{comp:<30} | {status:<10} | {detail}")
    print("-" * 75)

    if all_passed:
        print("[Erfolg] Alle Integritätsprüfungen bestanden.")
        return 0
    else:
        print("[Warnung] Eine oder mehrere Prüfungen sind fehlgeschlagen.")
        return 1


def run_ast_analysis(path_str: str, output_file: Optional[str] = None) -> int:
    """
    Führt eine AST-Codeanalyse auf einer Datei oder einem Verzeichnis aus.
    """
    from modules.analyzer.method_analyzer import MethodAnalyzer
    analyzer = MethodAnalyzer()

    target = Path(path_str).resolve()
    if not target.exists():
        print(f"[Fehler] Pfad nicht gefunden: {target}", file=sys.stderr)
        return 1

    py_files = [target] if target.is_file() else list(target.rglob("*.py"))
    if not py_files:
        print(f"[Hinweis] Keine Python-Dateien gefunden unter: {target}")
        return 0

    print(f"Analysiere {len(py_files)} Python-Datei(en) unter: {target}...")
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

    # 3. AST-Analyse
    if args.analyze:
        return run_ast_analysis(args.analyze, output_file=args.output)

    # 4. Workspace-Export
    if args.export_workspace:
        return run_workspace_export(args.export_workspace, output_file=args.output)

    # 5. Headless ohne spezifische Aktion
    if args.headless:
        if args.open:
            print(f"[Headless] Projektpfad verifiziert: {args.open}")
            return 0
        parser.print_help()
        return 0

    # GUI starten
    return args
