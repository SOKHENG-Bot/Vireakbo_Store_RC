from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CORS
    CORS_ORIGINS: List[str]
    CORS_CREDENTIALS: bool
    CORS_METHODS: List[str]
    CORS_HEADERS: List[str]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


getSettings = Settings()
