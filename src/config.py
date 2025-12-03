import os

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> str:
    dir = Path(__file__).parent.parent
    if os.getenv("TEST_ENV") == "docker":
        return str(dir / ".env.docker")
    return str(dir / ".env.local")


class Settings(BaseSettings):
    test_env: str

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    django_host: str
    django_port: str
    django_key: str

    model_config = SettingsConfigDict(env_file=get_env_file())


settings = Settings()
