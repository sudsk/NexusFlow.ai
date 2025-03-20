# NexusFlow.ai  

![NexusFlow.ai](docs/assets/logo.png)

NexusFlow.ai is a comprehensive agent orchestration platform that supports multiple AI frameworks (LangGraph, CrewAI, AutoGen, DSPy) through an adapter pattern.

## Architecture

![Architecture](docs/assets/architecture-diagram.svg)

NexusFlow uses a modular architecture with framework adapters that allow you to build flows using any supported orchestration framework.

## Features  

- **Multi-Framework Support**: Build flows using LangGraph (fully supported in MVP), with basic support for CrewAI, AutoGen, and DSPy  
- **Visual Flow Designer**: Drag-and-drop interface for creating agent workflows  
- **Flexible Tool Integration**: Register, configure, and use custom tools within your flows  
- **Execution Monitoring**: Track and visualize execution paths with real-time updates  
- **Flow Deployment**: Deploy flows as API endpoints for production use  
  
## Tool Registry  
  
NexusFlow includes a built-in tool registry that allows you to:  
  
- Register custom tools that can be used across different frameworks  
- Test tools individually before integrating them into flows  
- Manage tool compatibility with different frameworks  
- Configure framework-specific settings for each tool  
  
## Local Development Setup

### Environment Variables  
  
In addition to the database and API key settings, you can configure:  
  
- `DISABLE_AUTH=true` - Disables authentication for local development  
- `USE_MOCK_TOOLS=true` - Uses mock implementations for tools without API keys  
- `ALLOW_CODE_EXECUTION=false` - Controls whether code execution tools are enabled  
- `REACT_APP_USE_MOCK_API=true` - Enables mock API mode in the frontend  
  
### Prerequisites

- Python 3.9 or newer
- Node.js 16 or newer
- PostgreSQL 13 or newer

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nexusflow.git
   cd nexusflow
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL and API keys
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

6. Run the backend development server:
   ```bash
   python run.py
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env if needed (REACT_APP_API_URL=http://localhost:8000/api)
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`.

### Using Mock Mode

During development, you can use the mock API mode to work without a backend:

1. Set `REACT_APP_USE_MOCK_API=true` in your `.env` file
2. Or toggle mock mode in the login screen

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Working with Frameworks

### LangGraph

The primary framework supported in the MVP. To use LangGraph with NexusFlow:

1. Install LangGraph: `pip install langgraph`
2. Configure your OpenAI API key in `.env`
3. Create a new flow and select LangGraph as the framework
4. Add agents and tools to your flow
5. Configure agent roles and relationships
6. Test and deploy your flow

### CrewAI, AutoGen, and DSPy

Additional frameworks will be fully supported in future releases. Basic integration is available in the MVP.

## Deployment

### Local Docker Deployment

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the application at `http://localhost:3000`

### Production Deployment

For production environments, we recommend:

1. Setting up a proper PostgreSQL database
2. Using HTTPS for all communications
3. Implementing proper user authentication
4. Setting up monitoring and logging
5. Deploying behind a reverse proxy like Nginx

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to NexusFlow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



