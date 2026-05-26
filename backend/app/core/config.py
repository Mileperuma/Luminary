"""Application configuration loaded from environment variables.

Single source of truth for runtime config. Anything that varies between
local dev, staging, and production lives here.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_ENV: str = "development"
    APP_NAME: str = "Luminary"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg://luminary:luminary_dev_only@localhost:5432/luminary"

    # --- Auth ---
    JWT_SECRET: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60

    # --- LLM ---
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    LLM_DAILY_TOKEN_BUDGET: int = 200_000

    # --- External APIs ---
    GOOGLE_BOOKS_API_KEY: str | None = None
    TMDB_API_KEY: str | None = None
    OMDB_API_KEY: str | None = None
    GUARDIAN_API_KEY: str | None = None
    YOUTUBE_API_KEY: str | None = None

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use this everywhere instead of instantiating Settings()."""
    return Settings()
