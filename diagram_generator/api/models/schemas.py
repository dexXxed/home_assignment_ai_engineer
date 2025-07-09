"""
Additional schemas and data models for the diagram generator API
"""
from typing import Dict, Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a tool call from the LLM"""
    name: str = Field(..., description="Name of the tool to call")
    args: Dict[str, Any] = Field(..., description="Arguments for the tool call")
