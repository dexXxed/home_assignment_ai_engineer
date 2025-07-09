"""
Diagram Generator Service

A modular FastAPI service for generating architecture diagrams using AI
"""

from .api import app, get_app
from .core.config import settings

__version__ = settings.APP_VERSION

__all__ = [
    "app",
    "get_app",
    "settings"
]
