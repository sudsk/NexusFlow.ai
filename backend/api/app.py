# backend/api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from .routes import flow_routes, execution_routes, tool_routes

app = FastAPI(
    title="NexusFlow.ai API",
    description="API for the NexusFlow.ai agent orchestration platform",
    version="0.1.0",
    docs_url=None,  # Disable automatic docs
    redoc_url=None  # Disable automatic redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flow_routes.router)
app.include_router(execution_routes.router)
app.include_router(tool_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to NexusFlow.ai API"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="NexusFlow.ai API",
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui-bundle.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="NexusFlow.ai API",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title="NexusFlow.ai API",
        version="0.1.0",
        description="API for the NexusFlow.ai agent orchestration platform",
        routes=app.routes
    )
