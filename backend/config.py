import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    load_dotenv()

    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool

    SECRET: str | None

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    SQLALCHEMY_URL: Optional[PostgresDsn] = None

    @validator('POSTGRES_HOST', pre=True)
    def check_debug_mode(cls, value, values):
        if values.get('DEBUG'):
            return 'localhost'
        return value

    @validator('SECRET', pre=True)
    def set_secret(cls, value, values):
        if value is not None:
            return value

        if values.get('DEBUG'):
            load_dotenv('../.backend.env')
            return os.getenv('SECRET')

        raise Exception('miss secret')

    @validator('SQLALCHEMY_URL', pre=True)
    def get_sqlalchemy_url(cls, value, values):
        if isinstance(value, str):
            return value

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            port=str(values.get('POSTGRES_PORT')),
            path=f'/{values.get("POSTGRES_DB")}'
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
