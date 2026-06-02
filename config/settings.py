import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Price Intelligence Platform"
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Supabase Settings (Optional for local test if mock DB is fallback)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # ML Settings
    MODEL_REGISTRY_PATH: Path = Path(__file__).parent.parent / "ml" / "models"
    
    # Scraper Settings
    SCRAPE_INTERVAL_HOURS: int = 12
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()
