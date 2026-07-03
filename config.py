from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gas_url: str
    gas_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
