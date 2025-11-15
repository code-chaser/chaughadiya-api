from __future__ import annotations

from pathlib import Path

from flask import Flask

from chaughadiya_api.api.routes import api_bp
from chaughadiya_api.config import configure_logging, get_config
from chaughadiya_api.errors import register_error_handlers
from chaughadiya_api.keepalive import maybe_start_keepalive
from chaughadiya_api.pages.views import pages_bp

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    configure_logging(app.config.get("LOG_LEVEL", "INFO"))

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    register_error_handlers(app)
    maybe_start_keepalive(app)

    return app

