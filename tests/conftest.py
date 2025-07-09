"""
Test configuration and fixtures for the diagram generator service
"""
import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from diagram_generator.core.config import Settings
from diagram_generator.utils.gemini_client import GeminiClient


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """
    Create a temporary directory for test files
    
    Yields:
        str: Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_image_data() -> str:
    """
    Sample base64 encoded image data for testing
    
    Returns:
        str: Base64 encoded image data
    """
    # Simple 1x1 pixel PNG in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="


@pytest.fixture
def mock_gemini_client() -> Mock:
    """
    Mock Gemini client for testing
    
    Returns:
        Mock: Mock Gemini client instance
    """
    mock_client = Mock(spec=GeminiClient)
    mock_client.api_key = "test_api_key"
    mock_client.model_name = "test_model"
    mock_client.is_available.return_value = True
    return mock_client


@pytest.fixture
def mock_settings() -> Settings:
    """
    Mock settings for testing
    
    Returns:
        Settings: Test settings instance
    """
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"}):
        return Settings()


@pytest.fixture
def sample_diagram_request() -> dict:
    """
    Sample diagram request data for testing
    
    Returns:
        dict: Sample request data
    """
    return {
        "description": "Generate a microservices architecture with authentication and payment services"
    }


@pytest.fixture
def sample_tool_calls() -> list:
    """
    Sample tool calls for testing
    
    Returns:
        list: Sample tool calls
    """
    return [
        {"name": "create_canvas", "args": {"title": "Test Architecture"}},
        {"name": "add_node", "args": {"canvas_id": "test_canvas", "node_id": "api_gateway", "node_type": "api_gateway", "label": "API Gateway"}},
        {"name": "render_diagram", "args": {"canvas_id": "test_canvas"}}
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """
    Cleanup test files after each test
    """
    yield
    # Clean up any test files created during tests
    test_files = Path.cwd().glob("test_*.png")
    for file in test_files:
        try:
            file.unlink()
        except OSError:
            pass 