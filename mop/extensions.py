"""Flask extensions initialized without app (Application Factory Pattern)."""

from typing import Any
from flask import Flask, current_app
from flask_babel import Babel
from flask_caching import Cache

babel = Babel()
cache = Cache()

# pylint: disable=invalid-name
_default_app: Flask | None = None


def set_default_app(app: Flask) -> None:
    # pylint: disable=global-statement
    global _default_app
    _default_app = app


def get_app_config(key: str, default: Any = '') -> Any:
    try:
        return current_app.config.get(key, default)
    except RuntimeError:
        if _default_app is not None:
            return _default_app.config.get(key, default)
        return default
