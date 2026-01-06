"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "DHCP Admin"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./data/dhcp-admin.db"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Security Features (can be disabled)
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_SECURITY_HEADERS: bool = True
    ENABLE_CORS: bool = True

    # CORS
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:80"

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # DHCP Configuration
    DHCP_CONFIG_PATH: str = "/dhcp-config/dhcpd.conf"
    DOCKER_NETWORK_SUBNET: str = "172.18.0.0/16"  # Docker bridge network CIDR

    # Admin User (created on first run)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # Change this!
    ADMIN_EMAIL: str = "admin@localhost"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
