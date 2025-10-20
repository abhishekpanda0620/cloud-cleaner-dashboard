from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-south-1"
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = None
    
    # Server Configuration
    port: int = 8084
    host: str = "0.0.0.0"
    
    # Application Configuration
    app_name: str = "Cloud Cleaner API"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
