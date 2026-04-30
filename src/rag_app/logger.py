"""Production-grade centralized logging system for RAG application."""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log level constants
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LogConfig:
    """Centralized logging configuration."""

    # Default settings
    DEFAULT_LEVEL = logging.INFO
    FILE_LEVEL = logging.DEBUG
    CONSOLE_LEVEL = logging.INFO

    # Log formats
    DETAILED_FORMAT = (
        "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)-8s | "
        "%(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
    )
    SIMPLE_FORMAT = "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"

    # Date format
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Default log directory structure
    BASE_LOGS_DIR = Path("./logs")

    @classmethod
    def get_module_log_dir(cls, module_name: str) -> Path:
        """Get log directory for a module.

        Args:
            module_name: Name of the module (e.g., 'ingestion', 'retrieval')

        Returns:
            Path to module log directory
        """
        if module_name == "root":
            return cls.BASE_LOGS_DIR
        return cls.BASE_LOGS_DIR / module_name

    @classmethod
    def get_log_file_path(cls, logger_name: str) -> Path:
        """Get log file path for a logger.

        Args:
            logger_name: Logger name from __name__

        Returns:
            Path to log file
        """
        # Extract module name from logger name
        # e.g., "rag_app.ingestion.pdf_loader" -> "ingestion"
        parts = logger_name.split(".")
        if len(parts) >= 3 and parts[0] == "rag_app":
            module_name = parts[1]
        else:
            module_name = "root"

        log_dir = cls.get_module_log_dir(module_name)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Use component name or module name for log file
        if len(parts) >= 3:
            log_file_name = f"{parts[-1]}.log"
        else:
            log_file_name = f"{module_name}.log"

        return log_dir / log_file_name


def setup_logger(
    name: str,
    level: int = LogConfig.DEFAULT_LEVEL,
    enable_console: bool = True,
    enable_file: bool = True,
    log_file_max_bytes: int = 10 * 1024 * 1024,  # 10MB
    log_file_backup_count: int = 5,
) -> logging.Logger:
    """Setup a production-grade logger.

    Args:
        name: Logger name (typically __name__)
        level: Logging level
        enable_console: Enable console output
        enable_file: Enable file logging
        log_file_max_bytes: Max bytes per log file
        log_file_backup_count: Number of backup log files

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Don't add handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LogConfig.CONSOLE_LEVEL)
        console_formatter = logging.Formatter(LogConfig.SIMPLE_FORMAT, LogConfig.DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Rotating file handler
    if enable_file:
        try:
            log_file_path = LogConfig.get_log_file_path(name)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=log_file_max_bytes,
                backupCount=log_file_backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(LogConfig.FILE_LEVEL)
            file_formatter = logging.Formatter(LogConfig.DETAILED_FORMAT, LogConfig.DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            # Fallback: log warning to console if file logging fails
            logger.warning(f"Failed to setup file logging for {name}: {str(e)}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a production-grade logger.

    This is the main function to use for getting loggers throughout the application.

    Args:
        name: Logger name (use __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from rag_app.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    logger = logging.getLogger(name)

    # Setup if not already configured
    if not logger.handlers:
        setup_logger(name)

    return logger


def setup_root_logger(level: int = logging.INFO) -> logging.Logger:
    """Setup root logger for the entire application.

    This should be called once at application startup.

    Args:
        level: Logging level for root logger

    Returns:
        Root logger instance
    """
    return setup_logger("rag_app", level=level)


def disable_external_logging() -> None:
    """Disable verbose logging from external libraries.

    Call this to reduce noise from third-party libraries.
    """
    # Disable verbose library loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
