from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AgriTech Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./agritech.db"

    secret_key: str = "agritech-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    logstash_host: str = "logstash"
    logstash_port: int = 5044

    # Africa's Talking (USSD/SMS gateway)
    africastalking_username: str = "sandbox"
    africastalking_api_key: str = "test-api-key"

    # Open-Meteo (free satellite weather API)
    weather_api_url: str = "https://api.open-meteo.com/v1/forecast"

    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
