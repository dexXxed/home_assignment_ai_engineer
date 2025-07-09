"""
Tests for diagram_generator.core.config module
"""
import os
from unittest.mock import patch

import pytest

from diagram_generator.core.config import Settings


class TestSettings:
    """Test Settings class"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        settings = Settings()
        assert settings.APP_NAME == "AI Engineer Home Assignment - Enhanced Diagram Service"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.RELOAD is True
        assert settings.LOG_LEVEL == "INFO"
    
    def test_gemini_api_key_from_env(self):
        """Test that Gemini API key can be set"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = "test_key"
        assert settings.GEMINI_API_KEY == "test_key"
        settings.GEMINI_API_KEY = original_key
    
    def test_gemini_api_key_none_if_not_set(self):
        """Test that Gemini API key can be None"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = None
        assert settings.GEMINI_API_KEY is None
        settings.GEMINI_API_KEY = original_key
    
    def test_is_diagram_service_available_with_api_key(self):
        """Test that diagram service is available with API key"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = "test_key"
        assert settings.is_diagram_service_available is True
        settings.GEMINI_API_KEY = original_key
    
    def test_is_diagram_service_available_without_api_key(self):
        """Test that diagram service is not available without API key"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = None
        assert settings.is_diagram_service_available is False
        settings.GEMINI_API_KEY = original_key
    
    def test_is_diagram_service_available_with_empty_api_key(self):
        """Test that diagram service is not available with empty API key"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = ""
        assert settings.is_diagram_service_available is False
        settings.GEMINI_API_KEY = original_key
    
    def test_is_diagram_service_available_with_whitespace_api_key(self):
        """Test that diagram service is not available with whitespace API key"""
        settings = Settings()
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = "   "
        assert settings.is_diagram_service_available is False
        settings.GEMINI_API_KEY = original_key
    
    def test_app_description(self):
        """Test that app description is set correctly"""
        settings = Settings()
        assert settings.APP_DESCRIPTION == "Async FastAPI service with AI-powered diagram generation capabilities"
    
    def test_server_configuration(self):
        """Test server configuration values"""
        settings = Settings()
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.RELOAD is True
        assert settings.LOG_LEVEL == "INFO" 