from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
    )

    postgres_url: PostgresDsn = 'postgresql+asyncpg://mentor:123456@localhost:5532/mentor'
    log_level: str = "INFO"
    log_json: bool = True
