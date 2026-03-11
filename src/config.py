"""Configuration helpers for local and test environments."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    test_database_url: str
    app_env: str
    log_level: str


def load_settings(*, env: str | None = None) -> Settings:
    app_env = env if env is not None else (os.getenv("APP_ENV") or "development")
    env_file = ".env.test" if app_env == "test" else ".env"
    load_dotenv(dotenv_path=Path(env_file), override=True)

    return Settings(
        database_url=os.getenv("DATABASE_URL", "postgresql://replace-me"),
        test_database_url=os.getenv("TEST_DATABASE_URL", "sqlite:///./ops_test.db"),
        app_env=app_env,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
