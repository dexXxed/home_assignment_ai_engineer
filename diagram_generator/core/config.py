"""
Configuration module for the diagram generator service
"""
import os
from typing import Optional

from dotenv import load_dotenv


class Settings:
    """Application settings and configuration"""

    # Load environment variables
    load_dotenv()

    # API Configuration
    APP_NAME: str = "AI Engineer Home Assignment - Enhanced Diagram Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Async FastAPI service with AI-powered diagram generation capabilities"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = True
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # External API Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

    @property
    def is_diagram_service_available(self) -> bool:
        """
        Check if the diagram service is available
        
        Returns:
            bool: True if an API key is available, False otherwise
        """
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())


# Global settings instance
settings = Settings()
