#!/bin/bash
# setup.sh - Script to set up NexusFlow local development environment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up NexusFlow.ai development environment...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or newer.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 16 or newer.${NC}"
    exit 1
fi

# Check if NPM is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}NPM is not installed. Please install NPM.${NC}"
    exit 1
fi

# Setup backend
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy example environment file if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please update the .env file with your API keys and database configuration.${NC}"
fi

# Initialize database
echo "Initializing database with Alembic..."
alembic upgrade head

cd ..

# Setup frontend
echo -e "${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing NPM dependencies..."
npm install

# Copy example environment file if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

cd ..

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To run the backend:${NC}"
echo "cd backend"
echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "python run.py"
echo -e "${YELLOW}To run the frontend:${NC}"
echo "cd frontend"
echo "npm start"
echo -e "${YELLOW}Or use Docker Compose:${NC}"
echo "docker-compose up"
