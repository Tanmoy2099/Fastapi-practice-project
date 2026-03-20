from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "Practice Project"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate limiting (slowapi format: "N/period" e.g. "100/minute")
    rate_limit_default: str = "100/minute"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "practice_db"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_cache_ttl: int = 300

    class Config:
        env_file = ".env"


settings = Settings()
