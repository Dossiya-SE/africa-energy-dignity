"""Application settings."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from AED-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="AED_", env_file=".env", extra="ignore")
    env: str = "development"
    database_url: str = "sqlite+pysqlite:///./aed.db"
    database_echo: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    canonical_data_root: str = "data/canonical"
    asset_cache_root: str = "data/cache/geospatial"


@lru_cache
def get_settings() -> Settings:
    """Return the cached runtime settings."""
    return Settings()
