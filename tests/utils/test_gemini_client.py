"""
Tests for diagram_generator.utils.gemini_client module
"""
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from diagram_generator.utils.gemini_client import GeminiClient, create_gemini_client


class TestGeminiClient:
    """Test GeminiClient class"""

    def test_initialization(self):
        """Test client initialization"""
        client = GeminiClient("test_api_key", "test_model")
        assert client.api_key == "test_api_key"
        assert client.model_name == "test_model"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_initialization_with_defaults(self):
        """Test client initialization with default model"""
        client = GeminiClient("test_api_key")
        assert client.api_key == "test_api_key"
        assert client.model_name == "gemini-1.5-flash"

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_configure_genai_on_init(self, mock_model, mock_configure):
        """Test that Gemini API is configured on initialization"""
        GeminiClient("test_api_key")
        mock_configure.assert_called_once_with(api_key="test_api_key")
        mock_model.assert_called_once_with("gemini-1.5-flash")

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_content_success(self, mock_model):
        """Test successful content generation"""
        mock_response = Mock()
        mock_response.text = "Generated content"
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        result = await client.generate_content("test prompt")
        
        assert result == "Generated content"
        mock_model.return_value.generate_content_async.assert_called_once_with("test prompt")

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_content_timeout_with_retry(self, mock_model):
        """Test content generation with timeout and retry"""
        mock_model.return_value.generate_content_async = AsyncMock(side_effect=asyncio.TimeoutError())
        
        client = GeminiClient("test_api_key")
        with pytest.raises(asyncio.TimeoutError):
            await client.generate_content("test prompt")
        
        # Should retry max_retries times
        assert mock_model.return_value.generate_content_async.call_count == client.max_retries

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_content_exception_with_retry(self, mock_model):
        """Test content generation with exception and retry"""
        mock_model.return_value.generate_content_async = AsyncMock(side_effect=Exception("API Error"))
        
        client = GeminiClient("test_api_key")
        with pytest.raises(Exception):
            await client.generate_content("test prompt")
        
        # Should retry max_retries times
        assert mock_model.return_value.generate_content_async.call_count == client.max_retries

    @patch('google.generativeai.GenerativeModel')
    def test_generate_content_sync_success(self, mock_model):
        """Test successful synchronous content generation"""
        mock_response = Mock()
        mock_response.text = "Generated content"
        mock_model.return_value.generate_content = Mock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        result = client.generate_content_sync("test prompt")
        
        assert result == "Generated content"
        mock_model.return_value.generate_content.assert_called_once_with("test prompt")

    @patch('google.generativeai.GenerativeModel')
    def test_generate_content_sync_exception(self, mock_model):
        """Test synchronous content generation with exception"""
        mock_model.return_value.generate_content = Mock(side_effect=Exception("API Error"))
        
        client = GeminiClient("test_api_key")
        with pytest.raises(Exception):
            client.generate_content_sync("test prompt")

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_json_response_success(self, mock_model):
        """Test successful JSON response generation"""
        json_data = {"key": "value", "number": 42}
        mock_response = Mock()
        mock_response.text = json.dumps(json_data)
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        result = await client.generate_json_response("test prompt")
        
        assert result == json_data

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_json_response_with_json_block(self, mock_model):
        """Test JSON response generation with ```json block"""
        json_data = {"key": "value"}
        response_text = f"Here's the JSON:\n```json\n{json.dumps(json_data)}\n```"
        mock_response = Mock()
        mock_response.text = response_text
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        result = await client.generate_json_response("test prompt")
        
        assert result == json_data

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_json_response_with_explanation(self, mock_model):
        """Test JSON response generation with explanation text"""
        json_data = {"key": "value"}
        response_text = f"Here's an explanation. {json.dumps(json_data)} That's the JSON."
        mock_response = Mock()
        mock_response.text = response_text
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        result = await client.generate_json_response("test prompt")
        
        assert result == json_data

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_json_response_invalid_json(self, mock_model):
        """Test JSON response generation with invalid JSON"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON content"
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)
        
        client = GeminiClient("test_api_key")
        with pytest.raises(ValueError, match="Invalid JSON response from Gemini"):
            await client.generate_json_response("test prompt")

    def test_is_available_with_api_key(self):
        """Test is_available returns True with valid API key"""
        client = GeminiClient("test_api_key")
        assert client.is_available() is True

    def test_is_available_with_empty_api_key(self):
        """Test is_available returns False with empty API key"""
        client = GeminiClient("")
        assert client.is_available() is False

    def test_is_available_with_none_api_key(self):
        """Test is_available returns False with None API key"""
        client = GeminiClient(None)
        assert client.is_available() is False

    def test_is_available_with_whitespace_api_key(self):
        """Test is_available returns False with whitespace API key"""
        client = GeminiClient("   ")
        assert client.is_available() is False


class TestCreateGeminiClient:
    """Test create_gemini_client function"""

    @pytest.mark.asyncio
    async def test_create_client_with_defaults(self):
        """Test creating client with default parameters"""
        client = await create_gemini_client("test_api_key")
        assert isinstance(client, GeminiClient)
        assert client.api_key == "test_api_key"
        assert client.model_name == "gemini-1.5-flash"

    @pytest.mark.asyncio
    async def test_create_client_with_custom_model(self):
        """Test creating client with custom model"""
        client = await create_gemini_client("test_api_key", "custom_model")
        assert isinstance(client, GeminiClient)
        assert client.api_key == "test_api_key"
        assert client.model_name == "custom_model" 