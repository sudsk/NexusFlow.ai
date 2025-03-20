# backend/api/app.py (updated)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import flow_routes, execution_routes, tool_routes, framework_routes

app = FastAPI(
    title="NexusFlow.ai API",
    description="API for the NexusFlow.ai agent orchestration platform",
    version="0.1.0"
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
app.include_router(framework_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to NexusFlow.ai API"}
