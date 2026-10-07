from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Scrape API Platform"
    database_url: str = "sqlite+aiosqlite:///./scrape_api.db"
    jwt_secret: str = "change-this-in-production"
    jwt_expire_minutes: int = 60
    scrape_timeout_seconds: int = 15
    max_response_bytes: int = 5_000_000
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
