"""
Configuration module for the Auth0 FastAPI application.
Follows best practices for configuration management.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = Field(default="Auth0 Management API", env="API_TITLE")
    api_version: str = Field(default="v1", env="API_VERSION")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    debug: bool = Field(default=False, env="DEBUG")
    
    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="RS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Auth0 Configuration
    auth0_domain: str = Field(
        default="dev-b5oloevraq6545pr.us.auth0.com", env="AUTH0_DOMAIN"
    )
    auth0_api_audience: str = Field(
        default="https://dev-b5oloevraq6545pr.us.auth0.com/api/v2/",
        env="AUTH0_API_AUDIENCE"
    )
    auth0_management_token: Optional[str] = Field(
        default=None, env="AUTH0_MANAGEMENT_TOKEN"
    )
    auth0_client_id: Optional[str] = Field(default=None, env="AUTH0_CLIENT_ID")
    auth0_client_secret: Optional[str] = Field(
        default=None, env="AUTH0_CLIENT_SECRET"
    )
    
    # Auth Provider Configuration
    auth_provider: str = Field(default="auth0", env="AUTH_PROVIDER")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
