"""
Application settings using pydantic-settings.
Loads from environment variables / .env file.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "CafePOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:runtime@localhost:5432/cafepos_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # Admin seed
    ADMIN_EMAIL: str = "admin@cafepos.com"
    ADMIN_PASSWORD: str = "admin123"

    # SMTP Settings
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: str | None = None

    # Twilio Settings
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def sync_database_url(self) -> str:
        """Return synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
