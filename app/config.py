from __future__ import annotations

import os


class Config:
    """Base configuration for Flask app and database connection."""

    # Flask
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    WTF_CSRF_TIME_LIMIT: int | None = None

    # Database: default to MySQL at 127.0.0.1:3306 via PyMySQL
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "financial_platform_db")

    SQLALCHEMY_DATABASE_URI: str = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Server
    FLASK_RUN_HOST: str = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    FLASK_RUN_PORT: str = os.getenv("FLASK_RUN_PORT", "5000")
    FLASK_DEBUG: str = os.getenv("FLASK_DEBUG", "1")

