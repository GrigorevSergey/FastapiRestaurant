from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    SUPERUSER_PASSWORD: str
    DB_ECHO_LOG: bool = False

    class Config:
        env_file = ".env-dev"
        case_sensitive = True

settings = Settings()