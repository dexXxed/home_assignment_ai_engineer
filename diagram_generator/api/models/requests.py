"""
Request models for the diagram generator API
"""
from typing import Optional

from pydantic import BaseModel, Field


class DiagramRequest(BaseModel):
    """
    Request model for diagram generation
    """
    description: str = Field(..., description="Description of the diagram to generate")
    format: Optional[str] = Field(None, description="Optional format for the diagram")
