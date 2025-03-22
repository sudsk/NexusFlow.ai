# backend/api/middleware/error_middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

async def error_handler(request: Request, call_next):
    """
    Middleware to catch and format errors consistently
    """
    try:
        return await call_next(request)
    except Exception as e:
        # Log the full error with traceback
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a standardized error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal error occurred",
                "error_type": e.__class__.__name__,
                "error": str(e)
            }
        )
