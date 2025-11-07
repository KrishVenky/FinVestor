from __future__ import annotations

from typing import Any

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app() -> Flask:
    """Application factory for the Financial Investment Platform GUI."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuration
    from .config import Config

    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    csrf.init_app(app)

    # Blueprints
    from .routes import register_blueprints

    register_blueprints(app)

    # Jinja filters or globals can be registered here if needed

    # Ensure tables exist (safe no-ops if already created)
    with app.app_context():
        db.create_all()

    return app

