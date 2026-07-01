"""
Application configuration.

DATABASE_URL controls which database is used:
  - Postgres (production):  postgresql+psycopg2://user:pass@host:5432/lnhsp
  - SQLite (local/dev, default): sqlite:///./lnhsp.db

Set DATABASE_URL as an environment variable (or in a .env file) to point at
a real Postgres instance. If it's not set, the app falls back to a local
SQLite file so it can be run immediately without any external services.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "LNHSP API"
    api_v1_prefix: str = "/api/v1"

    # Default to SQLite for zero-config local dev; override with a Postgres
    # URL in production via the DATABASE_URL env var.
    database_url: str = "sqlite:///./lnhsp.db"

    # CORS - the Vite dev server default + common alternates
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    secret_key: str = "change-me-in-production"


settings = Settings()
