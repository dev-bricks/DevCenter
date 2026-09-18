# -*- coding: utf-8 -*-
"""
DevCenter - Runtime Logging
Zentrales Logging-System für DevCenter mit rotierendem Datei- und Konsolen-Handler.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from core.app_paths import get_log_file_path

DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3

_initialized = False


def setup_logging(
    level: str | int = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Initialisiert das Logging-System für DevCenter.

    Args:
        level: Log-Level als String (DEBUG, INFO, WARNING, ERROR) oder int
        log_to_file: Ob in die rotierende Datei geloggt werden soll
        log_to_console: Ob auf die Standardausgabe geloggt werden soll
        log_file: Optional abweichender Pfad zur Logdatei

    Returns:
        logging.Logger: Konfigurierter App-Logger
    """
    global _initialized

    if isinstance(level, str):
        level_int = getattr(logging, level.upper(), logging.INFO)
    else:
        level_int = level

    logger = logging.getLogger("devcenter")
    logger.setLevel(level_int)

    # Bereits vorhandene Handler bereinigen, um Doppel-Logs zu vermeiden
    for h in list(logger.handlers):
        logger.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass

    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level_int)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        target_path = log_file if log_file else get_log_file_path()
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=str(target_path),
                maxBytes=MAX_LOG_BYTES,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(level_int)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as err:
            logger.warning("Log-Datei unter %s konnte nicht geöffnet werden: %s", target_path, err)

    _initialized = True
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Liefert einen Logger im DevCenter-Namensraum.
    Falls logging noch nicht initialisiert wurde, wird es mit Standardeinstellungen gestartet.
    """
    if not _initialized:
        setup_logging()
    if name.startswith("devcenter."):
        return logging.getLogger(name)
    return logging.getLogger(f"devcenter.{name}")
