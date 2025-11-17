from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = str(Path(__file__).parent.parent / ".env")

print(f"ENV PATH: {env_path}")


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_container_host: str
    postgres_port: str
    django_host: str
    django_port: str
    django_key: str

    model_config = SettingsConfigDict(env_file=env_path)


settings = Settings()
