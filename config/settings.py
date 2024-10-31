from pathlib import Path

from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

BASE_DIR = Path(__file__).parent


class TelegramConfig(BaseModel):
    bot_token: str
    dispatchers_chat_id: int
    alert_chat_id: int


class SimpleOneConfig(BaseModel):
    url: str
    user: str
    password: str
    user_agent: str = 'Chrome/122.0.0.0'


class DatabaseConfig(BaseModel):
    url: PostgresDsn

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".prod.env",
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='APP_CONFIG__'
    )
    is_debug: bool = False
    simpleone: SimpleOneConfig
    db: DatabaseConfig
    telegram: TelegramConfig


settings = Settings()
