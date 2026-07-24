from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import create_engine

from ..settings import Settings


@lru_cache
def get_database_url() -> str:
    return Settings.model_validate({}).database_url


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_database_url())
