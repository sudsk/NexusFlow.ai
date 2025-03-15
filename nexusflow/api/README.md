# NexusFlow API Reference

## Overview

The NexusFlow API provides a RESTful interface for creating, managing, and executing agent workflows. These workflows (called "flows") orchestrate multiple AI agents to accomplish complex tasks through dynamic capability-driven interactions.

This document details the available endpoints, request and response formats, and authentication requirements for the NexusFlow API.

## Base URL

All API endpoints are relative to the base URL:

```
https://api.nexusflow.ai/api/nexusflow
```

For local development, the base URL is:

```
http://localhost:8000/api/nexusflow
```

## Authentication

The NexusFlow API uses bearer token authentication for protected endpoints. Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

API keys can be generated in the NexusFlow dashboard under Settings → API Keys.

## Response Format

All responses are in JSON format. Successful responses include the requested data, while error responses include an error message and status code:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "error_type"
}
```

## Endpoints

### Core Functionality

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/execute` | Execute a flow with provided configuration and input |
| GET | `/capabilities` | Get all available agent capabilities |
| POST | `/analyze-input` | Analyze input data to determine required capabilities |

### Flow Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/flows` | Create a new flow |
| GET | `/flows` | List all flows |
| GET | `/flows/{flow_id}` | Get details of a specific flow |
| PUT | `/flows/{flow_id}` | Update a specific flow |
| DELETE | `/flows/{flow_id}` | Delete a specific flow |
| POST | `/flows/{flow_id}/execute` | Execute a specific flow |

### Flow Deployment

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/flows/{flow_id}/deploy` | Deploy a flow as an API endpoint |
| POST | `/deployments/{deployment_id}/webhooks` | Create a webhook for a deployment |
| POST | `/deployed/{version}/{deployment_id}/execute` | Execute a deployed flow |

### Execution Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/executions/{execution_id}` | Get execution details |

---

## Detailed API Reference

### Execute Flow

Execute a flow with the given configuration and input.

```
POST /execute
```

#### Request Body

```json
{
  "flow_config": {
    "name": "Research Assistant",
    "description": "A research assistant flow",
    "agents": [
      {
        "name": "Coordinator",
        "capabilities": ["coordination", "planning"],
        "model_provider": "openai",
        "model_name": "gpt-4",
        "system_message": "You are a coordinator agent...",
        "temperature": 0.3,
        "tool_names": []
      },
      {
        "name": "Researcher",
        "capabilities": ["information_retrieval"],
        "model_provider": "openai",
        "model_name": "gpt-4",
        "tool_names": ["web_search"]
      }
    ],
    "max_steps": 10,
    "tools": {
      "web_search": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
          "query": {"type": "string", "description": "The search query"}
        }
      }
    }
  },
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  }
}
```

#### Response

```json
{
  "flow_id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "output": {
    "content": "Electric vehicles have several environmental impacts...",
    "output_type": "text",
    "metadata": {
      "agent_id": "writer",
      "agent_name": "Content Writer",
      "model": "openai/gpt-4"
    },
    "timestamp": "2025-03-15T14:25:30.123456Z"
  },
  "steps": 7,
  "execution_trace": [
    {
      "type": "start",
      "timestamp": "2025-03-15T14:22:30.123456Z",
      "step": 1,
      "input": {"query": "What are the environmental impacts of electric vehicles?"}
    },
    // Additional execution steps...
  ],
  "timestamp": "2025-03-15T14:25:30.654321Z"
}
```

### Get Capabilities

Get all available agent capabilities.

```
GET /capabilities
```

#### Response

```json
[
  {
    "type": "reasoning",
    "name": "General Reasoning",
    "description": "Ability to reason about general topics and answer questions",
    "parameters": {},
    "requires_tools": [],
    "provides_output": ["text"],
    "requires_input": ["query"],
    "examples": []
  },
  {
    "type": "information_retrieval",
    "name": "Information Retrieval",
    "description": "Ability to retrieve relevant information from external sources",
    "parameters": {},
    "requires_tools": ["web_search", "document_retrieval"],
    "provides_output": ["information", "sources", "citations"],
    "requires_input": ["query"],
    "examples": []
  },
  // Additional capabilities...
]
```

### Analyze Input

Analyze input data to determine required capabilities.

```
POST /analyze-input
```

#### Request Body

```json
{
  "query": "Write a Python function to calculate the Fibonacci sequence"
}
```

#### Response

```json
[
  "code_generation",
  "reasoning"
]
```

### Create Flow

Create a new flow.

```
POST /flows
```

#### Request Body

```json
{
  "flow_config": {
    "name": "Research Assistant",
    "description": "A research assistant that helps answer complex questions",
    "agents": [
      {
        "name": "Coordinator",
        "capabilities": ["coordination", "planning"],
        "model_provider": "openai",
        "model_name": "gpt-4",
        "system_message": "You are a coordinator agent...",
        "temperature": 0.3,
        "tool_names": []
      },
      // Additional agents...
    ],
    "max_steps": 10,
    "tools": {
      "web_search": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
          "query": {"type": "string", "description": "The search query"}
        }
      }
      // Additional tools...
    }
  }
}
```

#### Response

```json
{
  "id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "name": "Research Assistant",
  "description": "A research assistant that helps answer complex questions",
  "created_at": "2025-03-15T09:30:00.000Z",
  "updated_at": "2025-03-15T09:30:00.000Z",
  "config": {
    "name": "Research Assistant",
    "description": "A research assistant that helps answer complex questions",
    "agents": [
      // Agent configurations...
    ],
    "max_steps": 10,
    "tools": {
      // Tool configurations...
    }
  }
}
```

### List Flows

List all flows with pagination and optional filtering.

```
GET /flows
```

#### Query Parameters

- `limit` (optional): Maximum number of flows to return (default: 10, max: 100)
- `offset` (optional): Number of flows to skip (default: 0)
- `name` (optional): Filter flows by name

#### Response

```json
[
  {
    "id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
    "name": "Research Assistant",
    "description": "A research assistant that helps answer complex questions",
    "created_at": "2025-03-15T09:30:00.000Z",
    "updated_at": "2025-03-15T09:30:00.000Z",
    "config": {
      // Flow configuration...
    }
  },
  // Additional flows...
]
```

### Get Flow

Get details of a specific flow.

```
GET /flows/{flow_id}
```

#### Response

```json
{
  "id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "name": "Research Assistant",
  "description": "A research assistant that helps answer complex questions",
  "created_at": "2025-03-15T09:30:00.000Z",
  "updated_at": "2025-03-15T09:30:00.000Z",
  "config": {
    "name": "Research Assistant",
    "description": "A research assistant that helps answer complex questions",
    "agents": [
      // Agent configurations...
    ],
    "max_steps": 10,
    "tools": {
      // Tool configurations...
    }
  }
}
```

### Update Flow

Update a specific flow.

```
PUT /flows/{flow_id}
```

#### Request Body

```json
{
  "flow_config": {
    "name": "Enhanced Research Assistant",
    "description": "An improved research assistant that helps answer complex questions",
    "agents": [
      // Updated agent configurations...
    ],
    "max_steps": 15,
    "tools": {
      // Updated tool configurations...
    }
  }
}
```

#### Response

```json
{
  "id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "name": "Enhanced Research Assistant",
  "description": "An improved research assistant that helps answer complex questions",
  "created_at": "2025-03-15T09:30:00.000Z",
  "updated_at": "2025-03-15T10:15:00.000Z",
  "config": {
    // Updated flow configuration...
  }
}
```

### Delete Flow

Delete a specific flow.

```
DELETE /flows/{flow_id}
```

#### Response

Status code 204 (No Content) on success.

### Execute Flow by ID

Execute a specific flow.

```
POST /flows/{flow_id}/execute
```

#### Request Body

```json
{
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  },
  "options": {
    "max_steps": 12,
    "timeout": 60
  }
}
```

#### Response

```json
{
  "execution_id": "e1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "status": "pending",
  "result": null,
  "error": null
}
```

### Get Execution

Get execution details.

```
GET /executions/{execution_id}
```

#### Response

```json
{
  "execution_id": "e1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "status": "completed",
  "result": {
    "flow_id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
    "output": {
      "content": "Electric vehicles have several environmental impacts...",
      "output_type": "text",
      "metadata": {
        // Output metadata...
      },
      "timestamp": "2025-03-15T14:25:30.123456Z"
    },
    "steps": 7,
    "execution_trace": [
      // Execution steps...
    ],
    "timestamp": "2025-03-15T14:25:30.654321Z"
  },
  "error": null
}
```

### Deploy Flow

Deploy a flow as an API endpoint.

```
POST /flows/{flow_id}/deploy
```

#### Request Body

```json
{
  "version": "v1",
  "description": "Production deployment of the research assistant"
}
```

#### Response

```json
{
  "deployment_id": "d1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "api_key": "nf_a1b2c3d4e5f6g7h8i9j0",
  "endpoint_url": "/api/nexusflow/deployed/v1/d1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6/execute",
  "status": "active",
  "deployed_at": "2025-03-15T11:00:00.000Z"
}
```

### Create Webhook

Create a webhook for a deployment.

```
POST /deployments/{deployment_id}/webhooks
```

#### Request Body

```json
{
  "url": "https://example.com/webhook",
  "events": ["completed", "failed"],
  "secret": "your_webhook_secret"
}
```

#### Response

```json
{
  "id": "w1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "url": "https://example.com/webhook",
  "events": ["completed", "failed"],
  "secret": "your_webhook_secret",
  "created_at": "2025-03-15T11:30:00.000Z"
}
```

### Execute Deployed Flow

Execute a deployed flow.

```
POST /deployed/{version}/{deployment_id}/execute
```

#### Headers

```
Authorization: Bearer nf_a1b2c3d4e5f6g7h8i9j0
```

#### Request Body

```json
{
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  },
  "options": {
    "max_steps": 12,
    "timeout": 60
  }
}
```

#### Response

```json
{
  "execution_id": "e1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "status": "pending",
  "result": null,
  "error": null
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input parameters |
| 401 | Unauthorized - Missing or invalid API key |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Rate Limits

- 60 requests per minute for standard API keys
- 300 requests per minute for enterprise API keys
- Tool-specific rate limits may apply (e.g., web search has a limit of 100 searches per day)

## Webhooks

Webhooks allow you to receive real-time notifications about flow executions. When configured, NexusFlow will send POST requests to your specified URL when certain events occur.

### Webhook Events

- `completed`: Triggered when a flow execution completes successfully
- `failed`: Triggered when a flow execution fails
- `started`: Triggered when a flow execution starts
- `all`: Receive notifications for all events

### Webhook Payload

```json
{
  "execution_id": "e1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "deployment_id": "d1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "flow_id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "status": "completed",
  "timestamp": "2025-03-15T14:25:30.654321Z",
  "result": {
    // Execution result (for completed events)...
  },
  "error": "Error message" // (for failed events)
}
```

### Webhook Security

For security, NexusFlow includes a signature in the `X-NexusFlow-Signature` header. This signature is an HMAC-SHA256 hash of the request body, using your webhook secret as the key.

```python
import hmac
import hashlib

def verify_signature(payload_bytes, signature, secret):
    computed_signature = hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)
```

## SDKs and Client Libraries

NexusFlow provides official client libraries for several programming languages:

- [Python SDK](https://github.com/nexusflow/nexusflow-python)
- [JavaScript/TypeScript SDK](https://github.com/nexusflow/nexusflow-js)
- [Java SDK](https://github.com/nexusflow/nexusflow-java)

## Additional Resources

- [NexusFlow Documentation](https://docs.nexusflow.ai)
- [API Changelog](https://docs.nexusflow.ai/api/changelog)
- [Community Forum](https://community.nexusflow.ai)
- [Support](https://nexusflow.ai/support)
