"""
Response models for the diagram generator API
"""
from typing import Optional

from pydantic import BaseModel, Field


class DiagramResponse(BaseModel):
    """Response from diagram generation"""
    success: bool = Field(..., description="Whether the diagram was generated successfully")
    canvas_id: Optional[str] = Field(None, description="ID of the generated canvas")
    image_path: Optional[str] = Field(None, description="Path to the generated diagram image")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    reasoning: str = Field(..., description="Agent's reasoning for the diagram structure")
