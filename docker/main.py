#!/usr/bin/env python3
"""
Docker runner for the Diagram Generator Service
Optimized for containerized deployment
"""
import logging
import os
import sys
from pathlib import Path

import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the app from the modular structure
from diagram_generator import app, settings


def main():
    """
    Main entry point for Docker deployment
    """
    logger.info("Starting Diagram Generator Service")

    # Docker-specific environment checks
    gemini_key = os.getenv("GEMINI_API_KEY")
    port = settings.PORT
    host = settings.HOST  # Default to all interfaces in Docker

    if not gemini_key:
        logger.warning("GEMINI_API_KEY not set - diagram generation will be disabled")

    # Run the service with Docker-optimized settings
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # Disable reload in Docker
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
