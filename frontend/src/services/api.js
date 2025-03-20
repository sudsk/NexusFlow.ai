// frontend/src/services/api.js
import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Add centralized error handling
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred';
    console.error('API Error:', errorMessage);
    
    // For development mode, return mock data for certain endpoints
    if (process.env.NODE_ENV === 'development') {
      return handleMockResponses(error);
    }
    
    return Promise.reject(error);
  }
);

// Helper to create mock responses during development
const handleMockResponses = (error) => {
  const { config } = error;
  
  // Only handle GET requests for mocking
  if (config.method !== 'get') {
    return Promise.reject(error);
  }
  
  // Extract endpoint
  const endpoint = config.url.replace(/^\/api/, '');
  
  // Mock responses based on endpoint
  if (endpoint.match(/^\/flows\/[a-zA-Z0-9-]+$/)) {
    // Mock flow by ID
    const flowId = endpoint.split('/').pop();
    return Promise.resolve({
      data: {
        flow_id: flowId,
        name: 'Mock Flow',
        description: 'A mock flow for development',
        framework: 'langgraph',
        agents: [
          {
            agent_id: 'agent-1',
            name: 'Researcher',
            model_provider: 'openai',
            model_name: 'gpt-4',
            system_message: 'You are a research agent.',
            capabilities: ['information_retrieval', 'reasoning'],
            tool_names: ['web_search']
          },
          {
            agent_id: 'agent-2',
            name: 'Analyst',
            model_provider: 'anthropic',
            model_name: 'claude-3-opus',
            system_message: 'You are an analysis agent.',
            capabilities: ['data_analysis', 'reasoning'],
            tool_names: ['data_analysis']
          }
        ],
        tools: {
          'web_search': {
            description: 'Search the web for information',
            config: { use_async: true }
          },
          'data_analysis': {
            description: 'Analyze data and generate insights',
            config: { streaming: true }
          }
        },
        max_steps: 10,
        created_at: '2025-03-15T10:00:00Z',
        updated_at: '2025-03-15T10:00:00Z'
      }
    });
  }
  
  // Return the original error for endpoints we don't mock
  return Promise.reject(error);
};

// API endpoints
const apiService = {
  // Flow endpoints
  flows: {
    getAll: (params = {}) => api.get('/flows', { params }),
    getById: (flowId) => api.get(`/flows/${flowId}`),
    create: (flowData) => api.post('/flows', flowData),
    update: (flowId, flowData) => api.put(`/flows/${flowId}`, flowData),
    delete: (flowId) => api.delete(`/flows/${flowId}`),
    validate: (flowData) => api.post('/flows/validate', flowData),
    export: (flowId, targetFramework) => api.get(`/flows/${flowId}/export`, { 
      params: { target_framework: targetFramework } 
    }),
  },
  
  // Execution endpoints
  executions: {
    execute: (request) => api.post('/executions', request),
    getById: (executionId) => api.get(`/executions/${executionId}`),
    getByFlowId: (flowId, params = {}) => api.get(`/executions/flow/${flowId}`, { params }),
    getRecent: (limit = 10) => api.get('/executions', { params: { limit } }),
    getStats: () => api.get('/executions/stats'),
  },
  
  // Framework endpoints
  frameworks: {
    getAll: () => api.get('/frameworks'),
  },
  
  // Tool endpoints
  tools: {
    getAll: (params = {}) => api.get('/tools', { params }),
    getById: (toolId) => api.get(`/tools/${toolId}`),
    create: (toolData) => api.post('/tools', toolData),
    update: (toolId, toolData) => api.put(`/tools/${toolId}`, toolData),
    delete: (toolId) => api.delete(`/tools/${toolId}`),
  },
  
  // Capability endpoints
  capabilities: {
    getAll: () => api.get('/capabilities'),
    getById: (capabilityId) => api.get(`/capabilities/${capabilityId}`),
  },
  
  // Deployment endpoints
  deployments: {
    deploy: (flowId, deploymentData) => api.post(`/deployments/${flowId}`, deploymentData),
    getById: (deploymentId) => api.get(`/deployments/${deploymentId}`),
    getByFlowId: (flowId) => api.get(`/deployments/flow/${flowId}`),
    update: (deploymentId, deploymentData) => api.put(`/deployments/${deploymentId}`, deploymentData),
    delete: (deploymentId) => api.delete(`/deployments/${deploymentId}`),
    deactivate: (deploymentId) => api.post(`/deployments/${deploymentId}/deactivate`),
  },
  
  // Development helper to temporarily activate mock mode for testing
  _enableMockMode: (enable = true) => {
    if (enable) {
      api._originalNodeEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';
    } else if (api._originalNodeEnv) {
      process.env.NODE_ENV = api._originalNodeEnv;
      delete api._originalNodeEnv;
    }
  }
};

export default apiService;
