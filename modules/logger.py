"""
logger.py — Centralized logging for PyLinux Automator.
Logs both actions and errors with timestamps to separate files.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# ─── Log directory (relative to project root) ──────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _get_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    """Create and configure a named logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Avoid duplicate handlers on re-import

    logger.setLevel(level)
    log_path = LOG_DIR / filename
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# Two loggers: one for normal operations, one for errors only
action_logger = _get_logger("action", "actions.log", logging.INFO)
error_logger  = _get_logger("error",  "errors.log",  logging.ERROR)


def log_action(message: str) -> None:
    """Log a successful action or informational message."""
    action_logger.info(message)


def log_error(message: str) -> None:
    """Log an error or warning message."""
    error_logger.error(message)
    action_logger.error(message)   # also record in actions log


def log_section(title: str) -> None:
    """Write a visual separator to the action log."""
    sep = "─" * 60
    action_logger.info(sep)
    action_logger.info(f"  {title}")
    action_logger.info(sep)
