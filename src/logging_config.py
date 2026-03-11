"""Shared logging configuration helpers."""

from __future__ import annotations

import logging

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging once using the stdlib logger."""

    root_logger = logging.getLogger()
    normalized_level = getattr(logging, level.upper(), logging.INFO)

    if not root_logger.handlers:
        logging.basicConfig(level=normalized_level, format=_DEFAULT_FORMAT)
        return

    root_logger.setLevel(normalized_level)
    for handler in root_logger.handlers:
        handler.setLevel(normalized_level)
        if handler.formatter is None:
            handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
