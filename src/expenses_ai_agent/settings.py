from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    exchange_rate_api_key: str
    database_url: str = "sqlite:///expenses.db"

    model_config = SettingsConfigDict(env_file=".env")
