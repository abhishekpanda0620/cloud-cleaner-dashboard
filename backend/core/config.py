from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_account_id: Optional[str] = os.getenv("AWS_ACCOUNT_ID") 
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    notification_email_recipients: Optional[str] = os.getenv("NOTIFICATION_EMAIL_RECIPIENTS")
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: Optional[int] = os.getenv("SMTP_PORT")
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    sender_email: Optional[str] = os.getenv("SENDER_EMAIL")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL")
    
    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = os.getenv("REDIS_PORT", 6379)
    
    # Server Configuration
    port: int = os.getenv("PORT", 8084)
    host: str = os.getenv("HOST", "0.0.0.0")  # nosec B104
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # Application Configuration
    app_name: str = "Cloud Cleaner API"
    debug: bool = False
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Service Discovery Configuration
    discovery_scan_interval_hours: int = os.getenv("DISCOVERY_SCAN_INTERVAL_HOURS", 6)
    discovery_lookback_days: int = os.getenv("DISCOVERY_LOOKBACK_DAYS", 30)
    min_cost_threshold: float = os.getenv("MIN_COST_THRESHOLD", 0.0)  # Show all resources, including free tier
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from environment
    )

settings = Settings()
