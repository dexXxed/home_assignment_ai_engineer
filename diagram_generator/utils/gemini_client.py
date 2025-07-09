"""
Gemini API client utilities for the diagram generator service
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google Gemini API
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini client
        
        Args:
            api_key: Google Gemini API key
            model_name: Model name to use
        """
        self.api_key = api_key
        self.model_name = model_name

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

        # Add connection pooling and timeout settings
        self.timeout = 60.0
        self.max_retries = 3
        self.retry_delay = 1.0

    async def generate_content(self, prompt: str, timeout: Optional[float] = None) -> str:
        """
        Generate content using Gemini API with timeout and retry logic
        
        Args:
            prompt: Input prompt
            timeout: Optional timeout override
            
        Returns:
            str: Generated content
        """
        timeout = timeout or self.timeout

        for attempt in range(self.max_retries):
            try:
                # Use asyncio.wait_for for timeout handling
                response = await asyncio.wait_for(
                    self.model.generate_content_async(prompt),
                    timeout=timeout
                )
                return response.text
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except Exception as e:
                logger.error(f"Error generating content (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    def generate_content_sync(self, prompt: str) -> str:
        """
        Generate content using Gemini API (synchronous)
        
        Args:
            prompt: Input prompt
            
        Returns:
            str: Generated content
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    async def generate_json_response(self, prompt: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini API with improved error handling
        
        Args:
            prompt: Input prompt
            timeout: Optional timeout override
            
        Returns:
            Dict[str, Any]: Parsed JSON response
        """
        try:
            response = await self.generate_content(prompt, timeout)

            # Try to parse JSON from response
            # Look for JSON content between ```json and ``` or just parse directly
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
            else:
                json_content = response.strip()

            # Try to clean up common JSON issues
            json_content = json_content.replace("```", "").strip()

            # If the response starts with explanation, try to find JSON block
            if not json_content.startswith('{'):
                # Look for first { and last }
                start_idx = json_content.find('{')
                end_idx = json_content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_content = json_content[start_idx:end_idx + 1]

            return json.loads(json_content)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {response}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            logger.error(f"Error generating JSON response: {e}")
            raise

    def is_available(self) -> bool:
        """
        Check if the Gemini client is available
        
        Returns:
            bool: True if client is available, False otherwise
        """
        return self.api_key is not None and self.api_key.strip() != ""


async def create_gemini_client(api_key: str, model_name: str = "gemini-1.5-flash") -> GeminiClient:
    """
    Create a Gemini client instance
    
    Args:
        api_key: Google Gemini API key
        model_name: Model name to use
        
    Returns:
        GeminiClient: Configured client instance
    """
    return GeminiClient(api_key, model_name)
