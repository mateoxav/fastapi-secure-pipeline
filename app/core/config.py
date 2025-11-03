from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    project_name: str = "DevSecOps API"
    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Load from env (accepts CSV string or JSON list)
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], alias="ALLOWED_HOSTS")
    cors_origins: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ],
        alias="CORS_ORIGINS",
    )

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def _split_hosts_csv(cls, v):
        if isinstance(v, str):
            # handles: "localhost,127.0.0.1"
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_csv(cls, v):
        if isinstance(v, str) and not v.strip().startswith("["):
            # handles CSV string; for JSON use ["http://...","http://..."]
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

settings = Settings()
