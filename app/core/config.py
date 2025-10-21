from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Updated syntax for Pydantic v2 to load from .env
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    # Postgres DSN format for psycopg3: postgresql+psycopg://user:pass@host:port/dbname
    database_url: str = "postgresql+psycopg://appuser:apppass@localhost:5432/appdb"
    jwt_secret_key: str = "CHANGE_ME" # use a strong secret via env var in real deployments
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Added frontend test server port to prevent CORS errors
    cors_origins: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]

settings = Settings()