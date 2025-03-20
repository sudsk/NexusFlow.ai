#!/bin/bash
# test.sh - Script to run tests for NexusFlow backend

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running NexusFlow.ai backend tests...${NC}"

# Change to backend directory
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "Activated virtual environment."
else
    echo -e "${YELLOW}Virtual environment not found. Running with system Python.${NC}"
fi

# Set environment variables for testing
export USE_MOCK_TOOLS=true
export ALLOW_CODE_EXECUTION=false
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=nexusflow_test
export DB_USER=nexusflow-user
export DB_PASSWORD=nexusflow-password

# Check if pytest is installed
if ! python -c "import pytest" &> /dev/null; then
    echo -e "${YELLOW}Pytest not found. Installing...${NC}"
    pip install pytest pytest-asyncio
fi

# Run adapter tests
echo -e "${YELLOW}Running adapter tests...${NC}"
python -m pytest -xvs tests/test_backend.py

# Run repository tests
echo -e "${YELLOW}Running repository tests...${NC}"
python -m pytest -xvs tests/test_repositories.py

# Run service tests
echo -e "${YELLOW}Running service tests...${NC}"
python -m pytest -xvs tests/test_services.py

# Run API endpoint tests
echo -e "${YELLOW}Running API tests...${NC}"
python -m pytest -xvs tests/test_api.py

echo -e "${GREEN}All tests completed.${NC}"
