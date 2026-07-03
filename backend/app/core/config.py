from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Exodia"
    app_version: str = "0.1.0"
    api_prefix: str = ""
    database_url: str = Field(default="sqlite:///./exodia.db")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173", "null"]
    )
    plugins_dir: Path = Field(default=Path("./plugins"))
    http_timeout_seconds: float = 8.0
    max_concurrent_modules: int = 3
    safe_mode: bool = True
    auth_secret: str = "exodia-local-development-secret-change-me"
    auth_token_ttl_minutes: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EXODIA_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
