# -*- coding: utf-8 -*-
"""
DevCenter - Redigierter Workspace-Export
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.project_manager import ProjectConfig, ProjectManager
from core.settings_manager import SettingsManager

SCHEMA_NAME = "devcenter-workspace-v1"
APP_NAME = "DevCenter"
APP_VERSION = "1.0.0"

# B-005: Erlaubt Standard-Markdown-Aufgabenlisten (- [ ], * [ ], + [ ]) sowie bare [ ]
TASK_LINE_PATTERN = re.compile(r"^\s*(?:[-*+]\s+)?\[\s\]\s*(.+?)\s*$")
# Unterstützt P0: ... sowie [P0] ...
PRIORITY_PATTERN = re.compile(r"^(?:\[(P\d+)\]|(P\d+):)\s*(.+)$")

# B-006: PEP-508 Extras wie requests[security]>=2.28 oder pydantic[email,dotenv]
REQUIREMENT_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[([A-Za-z0-9_.,\s-]+)\])?\s*([<>=!~].+)?$")

WINDOWS_ABS_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
PATH_HINT_PATTERN = re.compile(r"[\\/]|^[A-Za-z]:")

FRAMEWORK_MAP = {
    "pyside6": "PySide6",
    "pyqt6": "PyQt6",
    "pyqt5": "PyQt5",
    "pyside2": "PySide2",
    "anthropic": "Anthropic",
    "keyring": "Keyring",
    "pyinstaller": "PyInstaller",
}
QT_FRAMEWORKS = {"PySide6", "PyQt6", "PyQt5", "PySide2"}

# B-007: Verzeichnisse, die bei der Dateizählung ignoriert werden
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    "releases",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".idea",
    ".vscode",
}


class PathRedactor:
    """Ersetzt lokale Pfade durch stabile Referenzen."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self._external_refs: Dict[str, str] = {}
        self._counters: Counter[str] = Counter()

    def redact(self, value: Any, preferred_prefix: str = "path") -> Any:
        """Redigiert bekannte Pfadstrings, alle anderen Werte bleiben unverändert."""
        if not isinstance(value, str) or not value:
            return value

        normalized = value.replace("\\", "/")
        if not self._looks_like_path(normalized):
            return value

        if not self._is_absolute_path(normalized):
            return normalized

        try:
            candidate = Path(value).resolve()
        except OSError:
            candidate = Path(value)

        try:
            relative = candidate.relative_to(self.project_root)
            rel_text = relative.as_posix()
            return f"project-1/{rel_text}" if rel_text else "project-1"
        except ValueError:
            return self._register_external_ref(value, preferred_prefix)

    def _register_external_ref(self, original: str, preferred_prefix: str) -> str:
        if original in self._external_refs:
            return self._external_refs[original]
        self._counters[preferred_prefix] += 1
        ref = f"{preferred_prefix}-{self._counters[preferred_prefix]}"
        self._external_refs[original] = ref
        return ref

    @staticmethod
    def _looks_like_path(value: str) -> bool:
        return bool(PATH_HINT_PATTERN.search(value))

    @staticmethod
    def _is_absolute_path(value: str) -> bool:
        return value.startswith("//") or value.startswith("/") or bool(WINDOWS_ABS_PATTERN.match(value))


def export_workspace(
    project: ProjectConfig,
    settings: SettingsManager,
    output_path: str,
    problems: Optional[Iterable[Any]] = None,
) -> Dict[str, Any]:
    """Schreibt einen redigierten Workspace-Export auf Platte und gibt ihn zurück."""
    payload = build_workspace_export(project, settings, problems=problems)
    Path(output_path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def build_workspace_export(
    project: ProjectConfig,
    settings: SettingsManager,
    problems: Optional[Iterable[Any]] = None,
    exported_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Erstellt den Workspace-Export als Python-Dictionary."""
    project_root = Path(project.path)
    redactor = PathRedactor(project_root)
    project_settings = _load_project_settings(project_root / ProjectManager.PROJECT_FILE)
    requirements = _parse_requirements(project_root / "requirements.txt")
    tasks = _parse_open_tasks(project_root / "AUFGABEN.txt")
    release_checklists = [
        {"title": task["title"], "status": task["status"]}
        for task in tasks
        if task.get("section", "").upper().startswith("PORTIERUNG")
    ]
    problem_list = list(problems or [])
    exported_at = exported_at or datetime.now(timezone.utc)

    payload = {
        "schema": SCHEMA_NAME,
        "schema_version": 1,
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "exported_at": exported_at.isoformat().replace("+00:00", "Z"),
        },
        "project": _build_project_payload(project, project_settings, requirements, redactor),
        "analysis": _build_analysis_payload(project_root, problem_list, redactor),
        "build": _build_build_payload(project, settings, redactor),
        "dependencies": {
            "requirements": requirements,
            "licenses": [],
        },
        "release": {
            "targets": ["github", "windows_store", "linux_direct", "web"],
            "checklists": release_checklists,
        },
        "tasks": tasks,
        "redactions": {
            "paths": True,
            "secrets": True,
            "source_content": True,
        },
    }
    return payload


def _load_project_settings(project_file: Path) -> Dict[str, Any]:
    if not project_file.exists():
        return {}
    try:
        return json.loads(project_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _build_project_payload(
    project: ProjectConfig,
    project_settings: Dict[str, Any],
    requirements: List[Dict[str, str]],
    redactor: PathRedactor,
) -> Dict[str, Any]:
    frameworks = _infer_frameworks(requirements)
    payload: Dict[str, Any] = {
        "name": project.name,
        "version": project.version,
        "path_ref": "project-1",
        "language": "python",
        "frameworks": frameworks,
        "has_devcenter_json": bool(project_settings),
    }
    if project.description:
        payload["description"] = project.description
    if project.main_file:
        payload["main_file_ref"] = redactor.redact(str(Path(project.path) / project.main_file))
    return payload


def _build_analysis_payload(
    project_root: Path,
    problems: List[Any],
    redactor: PathRedactor,
) -> Dict[str, Any]:
    warning_count = 0
    serialized_problems = []
    for problem in problems:
        severity = getattr(getattr(problem, "severity", ""), "value", getattr(problem, "severity", "info"))
        if severity == "warning":
            warning_count += 1
        serialized_problems.append(
            {
                "severity": severity or "info",
                "message": getattr(problem, "message", ""),
                "file_ref": redactor.redact(getattr(problem, "file_path", ""), "file"),
                "line": getattr(problem, "line", 0),
                "column": getattr(problem, "column", 0),
                "source": getattr(problem, "source", ""),
                "code": getattr(problem, "code", ""),
            }
        )

    return {
        "summary": {
            "files_indexed": _count_project_files(project_root),
            "problems_total": len(serialized_problems),
            "warnings_total": warning_count,
        },
        "problems": serialized_problems,
    }


def _build_build_payload(
    project: ProjectConfig,
    settings: SettingsManager,
    redactor: PathRedactor,
) -> Dict[str, Any]:
    project_build = dict(project.build_config or {})
    output_dir = project_build.get("output_dir") or settings.get("build.default_output_dir", "dist")
    payload: Dict[str, Any] = {
        "target": "windows-x64",
        "one_file": bool(project_build.get("one_file", settings.get("build.one_file", True))),
        "console": bool(project_build.get("console", settings.get("build.console_mode", True))),
        "output_ref": redactor.redact(output_dir, "output-dir"),
        "hidden_imports": list(project_build.get("hidden_imports", [])),
    }
    icon_path = project_build.get("icon")
    if icon_path:
        payload["icon_ref"] = redactor.redact(icon_path, "icon")
    return payload


def _parse_requirements(requirements_path: Path) -> List[Dict[str, Any]]:
    if not requirements_path.exists():
        return []

    requirements: List[Dict[str, Any]] = []
    try:
        content = requirements_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].split(";", 1)[0].strip()
        if not line or line.startswith(("-", ".")):
            continue
        match = REQUIREMENT_PATTERN.match(line)
        if not match:
            continue
        name, extras, specifier = match.groups()
        entry: Dict[str, Any] = {"name": name}
        if extras:
            entry["extras"] = [e.strip() for e in extras.split(",") if e.strip()]
        if specifier:
            entry["specifier"] = specifier.strip()
        requirements.append(entry)
    return requirements


def _infer_frameworks(requirements: List[Dict[str, Any]]) -> List[str]:
    detected = []
    for requirement in requirements:
        key = requirement["name"].lower()
        framework = FRAMEWORK_MAP.get(key)
        if framework and framework not in detected:
            detected.append(framework)
    # B-008: Nur PySide6 als Fallback einfügen, wenn kein anderes Qt-Framework erkannt wurde
    if not any(f in detected for f in QT_FRAMEWORKS):
        detected.insert(0, "PySide6")
    return detected


def _parse_open_tasks(tasks_path: Path) -> List[Dict[str, Any]]:
    if not tasks_path.exists():
        return []

    tasks: List[Dict[str, Any]] = []
    current_section = ""
    try:
        content = tasks_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            continue
        match = TASK_LINE_PATTERN.match(raw_line)
        if not match:
            continue
        text = match.group(1).strip()
        task: Dict[str, Any] = {"title": text, "status": "open"}
        if current_section:
            task["section"] = current_section
        priority_match = PRIORITY_PATTERN.match(text)
        if priority_match:
            prio = priority_match.group(1) or priority_match.group(2)
            task["priority"] = prio
            task["title"] = priority_match.group(3).strip()
        tasks.append(task)
    return tasks


def _count_project_files(project_root: Path) -> int:
    if not project_root.exists():
        return 0
    count = 0
    resolved_root = project_root.resolve()
    for root, dirs, files in os.walk(resolved_root):
        # In-place Pruning der ignorierten Ordner (verhindert zeitraubendes Traversieren von .venv/node_modules)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        count += len(files)
    return count
