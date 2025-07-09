"""
Diagram generation routes for the diagram generator API
"""
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import Response

from ...agents import create_diagram_agent
from ...api.models import DiagramRequest
from ...core.config import settings
from ...utils import file_exists

load_dotenv()

router = APIRouter()

# Module-level agent instance holder
_agent_instance: Optional[object] = None


async def get_agent():
    """
    Get or create the diagram agent instance
    
    Returns:
        object: Diagram agent instance
        
    Raises:
        HTTPException: If agent cannot be created
    """
    # Use module-level variable assignment instead of global
    current_module = sys.modules[__name__]

    if current_module._agent_instance is None:
        # Try to get an API key from multiple sources
        api_key = settings.GEMINI_API_KEY

        if not api_key:
            # Try additional environment variable names
            possible_keys = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"]
            for key_name in possible_keys:
                api_key = os.getenv(key_name)
                if api_key and api_key.strip():
                    break

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "GEMINI_API_KEY environment variable not set",
                    "message": "Please configure the Gemini API key to use diagram generation features",
                    "possible_env_vars": ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"],
                    "troubleshooting": "Try setting the environment variable: export GEMINI_API_KEY=your_api_key_here"
                }
            )

        current_module._agent_instance = await create_diagram_agent(api_key)

        if current_module._agent_instance is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create diagram agent",
                    "message": "Could not initialize the diagram generation service",
                    "api_key_found": bool(api_key),
                    "api_key_length": len(api_key) if api_key else 0
                }
            )

    return current_module._agent_instance


@router.post("/generate-diagram")
async def generate_diagram(
        description: str = Form(
            ...,
            description="Natural language description of the diagram to generate. For example: 'Generate a diagram of a microservices architecture' or 'Design a system for an e-commerce platform'",
            examples=["Generate a diagram of a microservices architecture",
                      "Design a system for an e-commerce platform"]
        )
):
    """
    Generate a diagram based on a natural language description and return the image directly
    
    Args:
        description: Natural language description of the diagram
        
    Returns:
        Response: PNG image of the generated diagram
    """
    if len(description.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Description must be at least 10 characters long"
        )

    try:
        agent = await get_agent()

        # Convert to the internal request format
        diagram_request = DiagramRequest(
            description=description
        )

        # Generate the diagram
        response = await agent.generate_diagram(diagram_request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate diagram: {response.error}"
            )

        # Return the image directly
        if response.image_path and file_exists(response.image_path):
            with open(response.image_path, "rb") as f:
                image_data = f.read()
            return Response(content=image_data, media_type="image/png")
        else:
            raise HTTPException(
                status_code=500,
                detail="Diagram was generated but image file was not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred during diagram generation: {str(e)}"
        )
