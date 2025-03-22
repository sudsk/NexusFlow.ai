# backend/api/middleware/auth_middleware.py
import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Define API key header
API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Load API keys from environment variables
# For development, you can set these in .env
# For production, use secure environment variables
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key")
API_KEYS = {
    ADMIN_API_KEY: {"user_id": "admin", "role": "admin"}
}

# Add more API keys from environment if available
if os.getenv("API_KEYS"):
    try:
        import json
        additional_keys = json.loads(os.getenv("API_KEYS"))
        API_KEYS.update(additional_keys)
    except Exception as e:
        logger.error(f"Failed to load additional API keys: {str(e)}")

async def verify_api_key(api_key: str = Depends(api_key_header)) -> dict:
    """
    Verify the API key and return the associated user info
    
    Args:
        api_key: API key from request header
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Check if we're in development mode (no auth)
    if os.getenv("DISABLE_AUTH", "").lower() == "true":
        # Return default user for development
        return {"user_id": "dev", "role": "admin"}
    
    # Check if API key is provided
    if not api_key:
        logger.warning("API key missing in request")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remove Bearer prefix if present
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    # Check if API key exists and is valid
    if api_key not in API_KEYS:
        logger.warning(f"Invalid API key: {api_key[:5]}...")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info associated with API key
    return API_KEYS[api_key]

async def get_admin_user(user_info: dict = Depends(verify_api_key)) -> dict:
    """
    Check if the user has admin privileges
    
    Args:
        user_info: User information from verify_api_key
        
    Returns:
        User information if user is admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if user_info.get("role") != "admin":
        logger.warning(f"Unauthorized admin access attempt by user {user_info.get('user_id')}")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user_info

class AuthMiddleware:
    """
    Middleware for API authentication
    This can be used to add authentication to all routes
    """
    
    async def __call__(self, request: Request, call_next):
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Skip auth for specific paths like health checks
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc", "/health"]:
            return await call_next(request)
        
        # Check if we're in development mode (no auth)
        if os.getenv("DISABLE_AUTH", "").lower() == "true":
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get(API_KEY_NAME)
        
        # Remove Bearer prefix if present
        if api_key and api_key.startswith("Bearer "):
            api_key = api_key[7:]
        
        # Validate API key
        if not api_key or api_key not in API_KEYS:
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            return HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Continue with the request
        return await call_next(request)
