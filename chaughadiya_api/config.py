from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, Type


class BaseConfig:
    """Base Flask configuration shared across environments."""

    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False

    KEEP_ALIVE_INTERVAL = int(os.getenv("KEEP_ALIVE_INTERVAL", "600"))
    ENABLE_KEEP_ALIVE = bool(os.getenv("RENDER_EXTERNAL_URL"))
    EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8080")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    ENABLE_KEEP_ALIVE = False


class ProductionConfig(BaseConfig):
    pass


CONFIG_MAP: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None) -> Type[BaseConfig]:
    if not name:
        env = os.getenv("FLASK_ENV") or os.getenv("ENVIRONMENT") or "production"
        return CONFIG_MAP.get(env.lower(), ProductionConfig)
    return CONFIG_MAP.get(name.lower(), ProductionConfig)


def configure_logging(level_name: str) -> None:  # pragma: no cover - glue logic
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")

