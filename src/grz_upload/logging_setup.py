"""
Module: logging_setup

This module provides functions for setting up logging configuration.
"""

import logging

from pathlib import Path
from grz_upload.constants import _PACKAGE_ROOT, _LOGGING_FORMAT, _LOGGING_DATEFMT

log = logging.getLogger(__name__)


def add_filelogger(file_path: Path = None, level: str = "INFO") -> None:
    """
    Add file logging for the specified package.

    This function configures a file logger to capture log messages
    for the package specified by _PACKAGE_ROOT. If no file path
    is provided, a default log file will be created in the user's
    home directory.

    :param file_path: Optional; the path to the log file. If None,
                      a default path will be used.
    :param level: Optional; the logging level. Default is 'INFO'.
                  Must be a valid logging level name (e.g., 'DEBUG', 'INFO').
    """
    package_logger = logging.getLogger(_PACKAGE_ROOT)

    if file_path is None:
        default_log_dir = Path.home() / "logs"
        default_log_dir.mkdir(parents=True, exist_ok=True)
        file_path = default_log_dir / f"{_PACKAGE_ROOT}.log"
        log.warning("No log file path provided, using default: %s", file_path)

    try:
        fh = logging.FileHandler(file_path)
        fh.setLevel(level.upper())
        fh.setFormatter(logging.Formatter(_LOGGING_FORMAT, _LOGGING_DATEFMT))
        package_logger.addHandler(fh)
        log.info(
            "File logger added for %s at %s with level %s.",
            package_logger.name,
            file_path,
            level.upper(),
        )
    except Exception as e:
        log.error("Failed to add file logger: %s", e)
