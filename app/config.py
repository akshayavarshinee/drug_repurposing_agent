"""
Application configuration settings.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Keys for agents
    OPENAI_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    
    # Agent processing
    AGENT_TIMEOUT: int = 300  # 5 minutes default
    ENABLE_AGENT_PROCESSING: bool = True
    
    # Paths
    @property
    def AGENTS_PATH(self) -> Path:
        """Get the path to the agents module."""
        return Path(__file__).parent.parent / "agents"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
