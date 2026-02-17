from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DB: Optional[str] = None
    MYSQL_DATABASE: Optional[str] = None
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = None
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
