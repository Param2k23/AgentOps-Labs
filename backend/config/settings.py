from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Enterprise Agent Lab"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # Upload directory
    upload_dir: str = Field(default="storage/uploads", alias="UPLOAD_DIR")

    # Async DSN used by SQLAlchemy at runtime.
    # Development defaults to SQLite (async driver), production uses PostgreSQL.
    database_url: str = Field(
        default="sqlite+aiosqlite:///agentlab.db",
        alias="DATABASE_URL",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Synchronous DSN for Alembic migrations.

        For SQLite development, return sync SQLite DSN.
        For PostgreSQL production, convert asyncpg URL to psycopg.
        """
        if self.database_url.startswith("sqlite+aiosqlite"):
            return self.database_url.replace("sqlite+aiosqlite", "sqlite")
        return self.database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
