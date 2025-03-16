"""
FastAPI server for NexusFlow.ai

This module provides a FastAPI server for the NexusFlow API, which can be used
to run the API as a standalone service or integrated into another FastAPI application.
"""

import logging
import os
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from nexusflow.api import router
from nexusflow.api.models import ErrorResponse
from nexusflow.utils import setup_logging

logger = logging.getLogger(__name__)

# Configure logging
setup_logging()

def create_app(
    title: str = "NexusFlow API",
    description: str = "Dynamic Agent Orchestration API",
    version: str = "0.1.0",
    debug: bool = False,
    allow_origins: List[str] = None
) -> FastAPI:
    """
    Create a FastAPI application for NexusFlow
    
    Args:
        title: API title
        description: API description
        version: API version
        debug: Whether to enable debug mode
        allow_origins: List of origins to allow CORS for
        
    Returns:
        FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        debug=debug,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Setup CORS
    if allow_origins is None:
        allow_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include NexusFlow router
    app.include_router(router)
    
    # Add exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                detail="Validation error",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                type="validation_error",
                errors=errors
            ).model_dump(),
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=exc.detail,
                status_code=exc.status_code,
                type="http_error"
            ).model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.exception(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                type="server_error"
            ).model_dump(),
        )
    
    # Add health check endpoint
    @app.get("/api/health", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "version": version}
    
    @app.get("/api/status", tags=["health"])
    async def status_check():
        """More detailed status check"""
        # Get environment information
        python_version = os.popen('python --version').read().strip()
        
        return {
            "status": "ok",
            "version": version,
            "environment": {
                "python_version": python_version,
                "debug_mode": debug
            }
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Get host from environment or use default
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Run server
    uvicorn.run(app, host=host, port=port)
