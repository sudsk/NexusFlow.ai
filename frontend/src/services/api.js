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
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred';
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
);

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
    export: (flowId, targetFramework) => api.get(`/flows/${flowId}/export`, { params: { target_framework: targetFramework } }),
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
  
  // Deployment endpoints
  deployments: {
    deploy: (flowId, deploymentData) => api.post(`/deployments/${flowId}`, deploymentData),
    getById: (deploymentId) => api.get(`/deployments/${deploymentId}`),
    getByFlowId: (flowId) => api.get(`/deployments/flow/${flowId}`),
    update: (deploymentId, deploymentData) => api.put(`/deployments/${deploymentId}`, deploymentData),
    delete: (deploymentId) => api.delete(`/deployments/${deploymentId}`),
    deactivate: (deploymentId) => api.post(`/deployments/${deploymentId}/deactivate`),
  },
};

export default apiService;
