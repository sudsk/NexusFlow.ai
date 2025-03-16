// ui/src/services/api.js
import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api/nexusflow',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for adding auth token, etc.
api.interceptors.request.use(
  (config) => {
    // Add authorization header if token exists
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error types
    if (error.response) {
      // Server responded with a status code outside the 2xx range
      console.error('API Error:', error.response.data);
      
      // Handle authentication errors
      if (error.response.status === 401) {
        // Redirect to login or refresh token
        // window.location.href = '/login';
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network Error:', error.request);
    } else {
      // Something happened in setting up the request
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
const apiService = {
  // Flows
  flows: {
    getAll: (params = {}) => api.get('/flows', { params }),
    getById: (flowId) => api.get(`/flows/${flowId}`),
    create: (flowConfig) => {
      return api.post('/flows', { flow_config: flowConfig });
    },
    update: (flowId, flowConfig) => api.put(`/flows/${flowId}`, { flow_config: flowConfig }),
    delete: (flowId) => api.delete(`/flows/${flowId}`),
    execute: (flowId, input, options = {}) => api.post(`/flows/${flowId}/execute`, { 
      input,
      options
    }),
  },
  
  // Executions
  executions: {
    getById: (executionId) => api.get(`/executions/${executionId}`),
    getByFlowId: (flowId, params = {}) => api.get(`/flows/${flowId}/executions`, { params }),
  },
  
  // Capabilities
  capabilities: {
    getAll: () => api.get('/capabilities'),
    analyzeInput: (input) => api.post('/analyze-input', input),
  },
  
  // Deployments
  deployments: {
    create: (flowId, version = 'v1', description = '') => api.post(`/flows/${flowId}/deploy`, {
      flow_id: flowId,
      version,
      description
    }),
    execute: (deploymentId, input, options = {}) => api.post(`/deployed/latest/${deploymentId}/execute`, {
      input,
      options
    }),
  },
  
  // Direct execution (without creating a flow)
  execute: (flowConfig, input) => api.post('/execute', {
    flow_config: flowConfig,
    input
  }),
  
  // Custom tools
  tools: {
    webSearch: (query, num_results = 5) => api.post('/tools/web_search', {
      query,
      num_results
    }),
    dataAnalysis: (data, analysis_type = 'descriptive', format = 'auto') => api.post('/tools/data_analysis', {
      data,
      analysis_type,
      format
    }),
    codeExecution: (code, timeout = 5, language = 'python') => api.post('/tools/code_execution', {
      code,
      timeout,
      language
    }),
  },
};

export default apiService;
