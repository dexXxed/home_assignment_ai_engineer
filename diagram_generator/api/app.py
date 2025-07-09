"""
Main FastAPI application for the diagram generator service
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .routes import diagram
from ..core.config import settings
from ..tools.mcp_tools import cleanup_all_temp_files

# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Diagram service available: {settings.is_diagram_service_available}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    
    # Clean up any resources
    try:
        cleanup_all_temp_files()
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include route modules
app.include_router(diagram.router, tags=["Diagrams"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and Docker health checks
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "diagram_service_available": settings.is_diagram_service_available
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions
    
    Args:
        request: Request object
        exc: Exception that occurred
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": exc.__class__.__name__
        }
    )



def get_app() -> FastAPI:
    """
    Get the FastAPI app instance
    
    Returns:
        FastAPI: The configured FastAPI app
    """
    return app
