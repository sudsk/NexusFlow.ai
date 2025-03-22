# backend/api/app.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
import logging
import time
import os

from .routes import flow_routes, execution_routes, tool_routes, framework_routes, deployment_routes
from .middleware.auth_middleware import AuthMiddleware

# Add to the beginning of backend/db/session.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nexusflow.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NexusFlow.ai API",
    description="API for the NexusFlow.ai agent orchestration platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False  # Add this line
)

# Configure CORS
origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
print(f"CORS Allowed Origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Expose all headers to the client
)

# Error handling middleware
@app.middleware("http")
async def error_handler(request: Request, call_next):
    """
    Middleware to catch and format errors consistently
    """
    start_time = time.time()
    try:
        response = await call_next(request)
        
        # Log request completion time for performance monitoring
        process_time = time.time() - start_time
        logger.debug(f"Request {request.method} {request.url.path} completed in {process_time:.4f}s")
        
        return response
    except Exception as e:
        # Log the full error with traceback
        logger.error(f"Unhandled exception in {request.method} {request.url.path}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a standardized error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred",
                "error_type": e.__class__.__name__,
                "error": str(e)
            }
        )

# Add authentication middleware if not in development mode
if os.environ.get("DISABLE_AUTH", "").lower() != "true":
    app.middleware("http")(AuthMiddleware())

# Custom handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for request validation errors
    """
    errors = []
    for error in exc.errors():
        # Format error messages to be more user-friendly
        loc = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error["msg"]
        errors.append(f"{loc}: {msg}")
    
    logger.warning(f"Validation error in {request.method} {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )

# Include routers
app.include_router(flow_routes.router, prefix="/api")
app.include_router(execution_routes.router, prefix="/api")
app.include_router(tool_routes.router, prefix="/api")
app.include_router(framework_routes.router, prefix="/api")
app.include_router(deployment_routes.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "api": "NexusFlow.ai"
    }

# API info endpoint
@app.get("/api")
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": "NexusFlow.ai API",
        "version": "0.1.0",
        "description": "Agent orchestration platform with support for multiple AI frameworks",
        "docs_url": "/docs",
        "frameworks": ["langgraph", "crewai", "autogen", "dspy"]
    }

# Root redirect to API info
@app.get("/")
async def root():
    """
    Root endpoint - redirects to API info
    """
    return await api_info()

# Startup event to initialize services and check components
@app.on_event("startup")
async def startup_event():
    """
    Initialization tasks when the API starts
    """
    from ..adapters.registry import get_adapter_registry
    from ..services.tool.registry_service import get_tool_registry
    
    try:
        # Check available adapters
        adapter_registry = get_adapter_registry()
        available_frameworks = adapter_registry.get_available_frameworks()
        logger.info(f"Available frameworks: {', '.join(available_frameworks.keys())}")
        
        # Check available tools
        tool_registry = get_tool_registry()
        tools = tool_registry.get_all_tools()
        logger.info(f"Registered tools: {len(tools)}")
        
        # Log successful startup
        logger.info("NexusFlow.ai API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all API requests
    """
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    return response
