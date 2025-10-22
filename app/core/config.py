from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # Pydantic v2 syntax for loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=True)

    project_name: str = "DevSecOps API"

    # Postgres DSN for psycopg3
    database_url: str = "postgresql+psycopg://appuser:apppass@db:5432/appdb"

    # JWT settings
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS origins
    cors_origins: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

settings = Settings()