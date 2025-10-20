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
    notification_email_recipients: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: Optional[str] = None
    
    # Server Configuration
    port: int = 8084
    host: str = "0.0.0.0"
    
    # Application Configuration
    app_name: str = "Cloud Cleaner API"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from environment
    )

settings = Settings()
