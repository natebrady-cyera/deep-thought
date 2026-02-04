"""
Application configuration using Pydantic settings.
Environment variables override defaults.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Deep Thought"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Database
    database_url: str = "sqlite:///./data/deep-thought.db"

    # SAML Authentication
    saml_idp_metadata_url: str
    saml_sp_entity_id: str
    saml_acs_url: Optional[str] = None  # Auto-constructed if not provided

    # Bootstrap
    bootstrap_admin_email: str

    # JWT
    secret_key: str = "change-me-in-production"  # Should be overridden
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # AWS Bedrock (for Claude)
    aws_bedrock_region: str = "us-east-1"
    aws_bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    aws_profile: str = "claude"  # AWS profile name for SSO
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Anthropic API (future)
    anthropic_api_key: Optional[str] = None

    # AI Configuration
    max_context_tokens: int = 100000  # Max tokens for context

    # Rate Limiting
    api_rate_limit: int = 100  # requests per minute per user

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
