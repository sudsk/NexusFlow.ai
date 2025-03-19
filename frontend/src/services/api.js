// frontend/src/services/api.js
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
const apiService = {
  // Flows
  flows: {
    getAll: (params = {}) => api.get('/flows', { params }),
    getById: (flowId) => api.get(`/flows/${flowId}`),
    create: (flowData) => api.post('/flows', flowData),
    update: (flowId, flowData) => api.put(`/flows/${flowId}`, flowData),
    delete: (flowId) => api.delete(`/flows/${flowId}`),
    execute: (flowId, input, framework = 'langgraph') => 
      api.post(`/flows/${flowId}/execute`, { input, framework }),
  },
  
  // Adapters/Frameworks
  frameworks: {
    list: () => api.get('/frameworks'),
    getDetails: (frameworkId) => api.get(`/frameworks/${frameworkId}`),
  },
  
  // Tools
  tools: {
    list: () => api.get('/tools'),
    getById: (toolId) => api.get(`/tools/${toolId}`),
  },
};

export default apiService;
