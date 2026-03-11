import logging

from src.logging_config import configure_logging


def test_configure_logging_updates_root_level():
    root_logger = logging.getLogger()
    previous_level = root_logger.level

    try:
        configure_logging("DEBUG")
        assert root_logger.level == logging.DEBUG
    finally:
        root_logger.setLevel(previous_level)
