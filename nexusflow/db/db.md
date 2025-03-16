# Database Integration for NexusFlow

This guide outlines the steps to integrate the database components with the rest of your NexusFlow application. The database layer uses SQLAlchemy with PostgreSQL.

## 1. Setup Database Connection

First, let's make sure your `.env` file is configured correctly with database credentials. This file should not be committed to version control, so you should use `.env.example` as a template.

```
# Database settings
export DB_HOST=127.0.0.1  # Use Cloud SQL proxy for local development
export DB_PORT=5432
export DB_NAME=nexusflow
export DB_USER=nexusflow-user
export DB_PASSWORD=SECURE_PASSWORD
```

## 2. Create Database Initialization Module

Create a new file `nexusflow/db/__init__.py` to initialize the database components:

```python
"""
Database components for NexusFlow.ai

This package contains database models and repositories for the NexusFlow system.
"""

from nexusflow.db.session import engine, Session, get_db
from nexusflow.db.models import Base
from nexusflow.db.repositories import (
    FlowRepository,
    ExecutionRepository,
    DeploymentRepository,
    WebhookRepository
)

# Initialize database if needed
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

__all__ = [
    'init_db',
    'Session',
    'get_db',
    'FlowRepository',
    'ExecutionRepository',
    'DeploymentRepository',
    'WebhookRepository',
]
```

## 3. Update Main Application Initialization

Update your main application file to initialize the database when the application starts:

```python
# In your main application file (e.g., nexusflow/main.py or app.py)
import logging
from fastapi import FastAPI
from nexusflow.api.server import create_app
from nexusflow.db import init_db

logger = logging.getLogger(__name__)

def start_application():
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Continue anyway, as tables might already exist
    
    # Create FastAPI application
    app = create_app()
    return app

app = start_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. Update API Routes to Use Database Repositories

Now, update your API routes to use the database repositories instead of in-memory storage. Here's an example for the flows routes:

```python
# In nexusflow/api/routes.py

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from nexusflow.db.session import get_db
from nexusflow.db.repositories import FlowRepository, ExecutionRepository, DeploymentRepository

# Modify the routes to use DB repositories
@router.get("/flows", response_model=List[FlowResponse])
async def list_flows(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List flows
    
    Args:
        limit: Maximum number of flows to return
        offset: Number of flows to skip
        name: Filter by name (optional)
        db: Database session
        
    Returns:
        List of flows
    """
    try:
        # Use FlowRepository instead of in-memory flows_db
        repository = FlowRepository(db)
        flows = repository.get_all(skip=offset, limit=limit, name=name)
        
        return [FlowResponse(**flow.__dict__) for flow in flows]
    except Exception as e:
        logger.exception(f"Error listing flows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/flows", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    request: FlowCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new flow
    
    Args:
        request: Flow creation request
        db: Database session
        
    Returns:
        Created flow
    """
    try:
        repository = FlowRepository(db)
        
        # Prepare flow data
        flow_data = {
            "name": request.flow_config.name,
            "description": request.flow_config.description,
            "config": request.flow_config.model_dump()
        }
        
        # Create flow in database
        flow = repository.create(flow_data)
        
        # Convert to response model
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            description=flow.description,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            config=FlowConfig(**flow.config)
        )
    except Exception as e:
        logger.exception(f"Error creating flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Similarly update other routes (get_flow, update_flow, delete_flow, etc.)
```

## 5. Implement Background Tasks with Database Storage

For background execution tasks, update the implementation to use the database:

```python
async def execute_flow_background(
    flow_id: str,
    execution_id: str,
    input_data: Dict[str, Any],
    options: Dict[str, Any] = None,
    deployment_id: Optional[str] = None,
    db: Session = None
):
    """
    Execute a flow in the background
    
    Args:
        flow_id: ID of the flow
        execution_id: ID of the execution
        input_data: Input data for the flow
        options: Execution options
        deployment_id: ID of the deployment (if any)
        db: Database session
    """
    options = options or {}
    
    # Create a new database session if not provided
    if db is None:
        db = Session()
    
    try:
        # Get repositories
        execution_repo = ExecutionRepository(db)
        flow_repo = FlowRepository(db)
        
        # Update execution status
        execution_repo.update(execution_id, {"status": "running"})
        
        # Get flow configuration
        flow = flow_repo.get_by_id(flow_id)
        if not flow:
            execution_repo.update(execution_id, {
                "status": "failed",
                "completed_at": datetime.utcnow(),
                "error": f"Flow with ID {flow_id} not found"
            })
            return
            
        flow_config = FlowConfig(**flow.config)
        
        # Create agents and execute flow
        # ... rest of execution logic remains the same

        # Update execution record on completion
        execution_repo.update(execution_id, {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "result": result
        })
        
        # Send webhook notifications if needed
        if deployment_id:
            await send_webhook_notifications(
                deployment_id=deployment_id,
                execution_id=execution_id,
                status="completed",
                result=result,
                db=db
            )
    
    except Exception as e:
        logger.exception(f"Error executing flow in background: {str(e)}")
        
        # Update execution record with error
        try:
            execution_repo.update(execution_id, {
                "status": "failed",
                "completed_at": datetime.utcnow(),
                "error": str(e)
            })
            
            # Send webhook notifications if needed
            if deployment_id:
                await send_webhook_notifications(
                    deployment_id=deployment_id,
                    execution_id=execution_id,
                    status="failed",
                    error=str(e),
                    db=db
                )
        except Exception as update_error:
            logger.error(f"Error updating execution record: {str(update_error)}")
    
    finally:
        # Close the session if we created it
        if db is not None:
            db.close()
```

## 6. Update FastAPI Dependency Injection

Finally, make sure your FastAPI application is set up to use the database session properly:

```python
# In nexusflow/api/server.py

from nexusflow.db.session import get_db

def create_app(...):
    # ... existing code ...
    
    # Add database session dependency
    app.dependency_overrides[get_db] = get_db
    
    # ... rest of function ...
```

## 7. Running Migrations

Before starting your application, you need to run the database migrations to create the tables:

```bash
# Set your environment variables
source .env

# Run migrations
python -m nexusflow.db.migrations
```

## 8. Error Handling and Validation

Make sure to add proper error handling for database operations:

```python
# Example of error handling for database operations
try:
    # Database operation
    result = repository.some_operation()
    return result
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error: {str(e)}"
    )
```

## 9. Testing Database Integration

Create a simple test script to verify the database integration:

```python
# test_db.py
import asyncio
from nexusflow.db import init_db, Session
from nexusflow.db.repositories import FlowRepository

async def test_database():
    # Initialize database
    init_db()
    
    # Create a session
    session = Session()
    
    try:
        # Try to create a flow
        flow_repo = FlowRepository(session)
        flow = flow_repo.create({
            "name": "Test Flow",
            "description": "A test flow",
            "config": {
                "name": "Test Flow",
                "description": "A test flow",
                "agents": [],
                "max_steps": 10
            }
        })
        
        print(f"Created flow with ID: {flow.id}")
        
        # Fetch the flow
        fetched_flow = flow_repo.get_by_id(flow.id)
        print(f"Fetched flow: {fetched_flow.name}")
        
        # Cleanup (optional for test)
        flow_repo.delete(flow.id)
        print("Flow deleted")
        
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(test_database())
```

This should provide a good foundation for integrating your database components with the rest of your application.
