import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(
    level: str,
    path: Path,
    max_bytes: int = 1_048_576,
    backup_count: int = 3,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[file_handler, console_handler],
        force=True,
    )