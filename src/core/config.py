from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env-dev", case_sensitive=True)
    
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
    REDIS_HOST: str
    REDIS_PORT: int
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str
    MENU_SERVICE_URL: str
    USER_SERVICE_URL: str
    CLOUDPAYMENTS_PUBLIC_ID: str
    CLOUDPAYMENTS_API_SECRET: str
    PAYMENT_SERVICE_URL: str

settings = Settings()