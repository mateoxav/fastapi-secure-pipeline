from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # Postgres DSN format for psycopg3: postgresql+psycopg://user:pass@host:port/dbname
    database_url: str = "postgresql+psycopg://appuser:apppass@localhost:5432/appdb"
    jwt_secret_key: str = "CHANGE_ME"  # use a strong secret via env var in real deployments
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: List[str] = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = True

settings = Settings()

