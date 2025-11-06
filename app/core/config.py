import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl, field_validator
from typing import List, Any

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    project_name: str = "DevSecOps API"
    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    allowed_hosts: List[str] = Field(..., alias="ALLOWED_HOSTS")
    cors_origins: List[AnyHttpUrl] = Field(..., alias="CORS_ORIGINS")

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_hosts(cls, v: Any):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

settings = Settings()
