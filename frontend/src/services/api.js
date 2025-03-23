// frontend/src/services/api.js
import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // Add timeout to prevent infinite loading states
  timeout: 30000,
});

// Check if using mock API (for development without backend)
const useMockApi = process.env.REACT_APP_USE_MOCK_API === 'true';

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Get API key from localStorage if available
    const apiKey = localStorage.getItem('nexusflow_api_key');
    if (apiKey) {
      config.headers['Authorization'] = `Bearer ${apiKey}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Get error details
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred';
    const errorStatus = error.response?.status;
    
    // Log error details
    console.error(`API Error (${errorStatus}):`, errorMessage);
    
    // Handle authentication errors
    if (errorStatus === 401) {
      // Clear invalid credentials
      localStorage.removeItem('nexusflow_api_key');
      
      // If not on login page, redirect to login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    // For development mode with mock API enabled, return mock data
    if (useMockApi) {
      return handleMockResponses(error);
    }
    
    return Promise.reject(error);
  }
);

// Helper to create mock responses during development
const handleMockResponses = (error) => {
  const { config } = error;
  const { method, url } = config;
  
  console.log(`[Mock API] ${method.toUpperCase()} ${url}`);
  
  // Extract endpoint
  const endpoint = url.replace(/^\/api/, '');
  
  // Mock GET responses
  if (method === 'get') {
    // Flow endpoints
    if (endpoint === '/flows') {
      return Promise.resolve({
        data: {
          items: [
            {
              flow_id: '1',
              name: 'Research Assistant',
              description: 'Performs research tasks',
              framework: 'langgraph',
              created_at: '2025-03-15T10:00:00Z',
              updated_at: '2025-03-15T10:00:00Z',
              agents: [
                {
                  agent_id: 'agent-1',
                  name: 'Researcher',
                  model_provider: 'openai',
                  model_name: 'gpt-4',
                },
                {
                  agent_id: 'agent-2',
                  name: 'Analyst',
                  model_provider: 'anthropic',
                  model_name: 'claude-3-opus',
                }
              ]
            },
            {
              flow_id: '2',
              name: 'Customer Support',
              description: 'Handles customer inquiries',
              framework: 'crewai',
              created_at: '2025-03-14T15:30:00Z',
              updated_at: '2025-03-14T15:30:00Z',
              agents: [
                {
                  agent_id: 'agent-1',
                  name: 'Support Lead',
                  model_provider: 'openai',
                  model_name: 'gpt-4',
                },
                {
                  agent_id: 'agent-2',
                  name: 'Technical Expert',
                  model_provider: 'anthropic',
                  model_name: 'claude-3-opus',
                }
              ]
            }
          ],
          total: 2
        }
      });
    }
    
    if (endpoint.match(/^\/flows\/[a-zA-Z0-9-]+$/)) {
      // Mock flow by ID
      const flowId = endpoint.split('/').pop();
      return Promise.resolve({
        data: {
          flow_id: flowId,
          name: flowId === '1' ? 'Research Assistant' : 'Mock Flow',
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
    
    // Framework endpoints
    if (endpoint === '/frameworks') {
      return Promise.resolve({
        data: {
          langgraph: {
            multi_agent: true,
            parallel_execution: true,
            tools: true,
            streaming: true,
            visualization: true
          },
          crewai: {
            multi_agent: true,
            parallel_execution: false,
            tools: true,
            streaming: false,
            visualization: true
          }
        }
      });
    }
    
    // Tool endpoints
    if (endpoint === '/tools') {
      return Promise.resolve({
        data: {
          items: [
            {
              id: '1',
              name: 'web_search',
              description: 'Search the web for information',
              parameters: {
                type: 'object',
                properties: {
                  query: {
                    type: 'string',
                    description: 'The search query',
                  },
                },
                required: ['query'],
              },
              is_enabled: true,
              metadata: {
                category: 'utility',
                compatible_frameworks: ['langgraph', 'crewai', 'autogen'],
              },
              framework_config: {
                langgraph: {
                  use_async: true,
                  streaming: false,
                },
                crewai: {
                  allow_delegation: true,
                }
              }
            },
            {
              id: '2',
              name: 'data_analysis',
              description: 'Analyze data and generate insights',
              parameters: {
                type: 'object',
                properties: {
                  data_source: {
                    type: 'string',
                    description: 'URL or path to the data source',
                  },
                  analysis_type: {
                    type: 'string',
                    enum: ['descriptive', 'exploratory', 'predictive'],
                  },
                },
                required: ['data_source'],
              },
              is_enabled: true,
              metadata: {
                category: 'data_processing',
                compatible_frameworks: ['langgraph', 'crewai', 'autogen', 'dspy'],
              },
              framework_config: {
                langgraph: {
                  use_async: true,
                  streaming: false,
                },
                crewai: {
                  allow_delegation: false,
                }
              }
            }
          ],
          total: 2
        }
      });
    }
    
    // Capability endpoints
    if (endpoint === '/capabilities') {
      return Promise.resolve({
        data: [
          { type: 'reasoning', name: 'General Reasoning' },
          { type: 'information_retrieval', name: 'Information Retrieval' },
          { type: 'code_generation', name: 'Code Generation' },
          { type: 'data_analysis', name: 'Data Analysis' },
          { type: 'summarization', name: 'Summarization' }
        ]
      });
    }
    
    // Execution endpoints
    if (endpoint.match(/^\/executions\/[a-zA-Z0-9-]+$/)) {
      const executionId = endpoint.split('/').pop();
      return Promise.resolve({
        data: {
          id: executionId,
          flow_id: '1',
          flow_name: 'Research Assistant',
          framework: 'langgraph',
          status: 'completed',
          started_at: '2025-03-15T10:30:00Z',
          completed_at: '2025-03-15T10:32:00Z',
          input: { query: "What are the latest developments in AI?" },
          result: { 
            output: {
              content: "The latest developments in AI include advancements in multimodal models, more efficient training techniques, and applications in scientific research. Large language models continue to evolve with improvements in reasoning capabilities and specialized domain knowledge."
            }
          },
          steps: 7,
          execution_trace: [
            {
              step: 1,
              agent_id: 'agent-1',
              agent_name: 'Researcher',
              type: 'agent_execution',
              input: { query: "What are the latest developments in AI?" },
              output: {
                content: "I'll search for the latest developments in AI.",
                metadata: { model: "openai/gpt-4" }
              },
              timestamp: "2025-03-15T10:30:10Z"
            },
            {
              step: 2,
              agent_id: 'agent-1',
              agent_name: 'Researcher',
              type: 'tool_execution',
              input: { query: "latest developments in artificial intelligence 2025" },
              output: {
                content: "Search results: 1. Multimodal AI models gaining prominence. 2. New training techniques reducing computational requirements. 3. Breakthroughs in AI for scientific research.",
                metadata: { tool: "web_search" }
              },
              timestamp: "2025-03-15T10:30:30Z"
            },
            {
              step: 3,
              agent_id: 'agent-1',
              agent_name: 'Researcher',
              type: 'delegation',
              decision: {
                action: "delegate",
                target: "agent-2",
                reasoning: "Need to analyze the search results"
              },
              timestamp: "2025-03-15T10:30:45Z"
            },
            {
              step: 4,
              agent_id: 'agent-2',
              agent_name: 'Analyst',
              type: 'agent_execution',
              input: { search_results: "1. Multimodal AI models gaining prominence. 2. New training techniques reducing computational requirements. 3. Breakthroughs in AI for scientific research." },
              output: {
                content: "Based on the search results, I'll analyze the key trends in AI development.",
                metadata: { model: "anthropic/claude-3-opus" }
              },
              timestamp: "2025-03-15T10:31:00Z"
            },
            {
              step: 5,
              agent_id: 'agent-2',
              agent_name: 'Analyst',
              type: 'tool_execution',
              input: { data_source: "search_results", analysis_type: "descriptive" },
              output: {
                content: "Analysis: The major trends in AI development for 2025 focus on three areas: 1) Multimodal models that can process diverse types of data, 2) Efficiency improvements in training and inference, and 3) Specialized applications in scientific domains.",
                metadata: { tool: "data_analysis" }
              },
              timestamp: "2025-03-15T10:31:30Z"
            },
            {
              step: 6,
              agent_id: 'agent-2',
              agent_name: 'Analyst',
              type: 'agent_execution',
              input: { analysis: "Analysis: The major trends in AI development for 2025 focus on three areas: 1) Multimodal models that can process diverse types of data, 2) Efficiency improvements in training and inference, and 3) Specialized applications in scientific domains." },
              output: {
                content: "The latest developments in AI include advancements in multimodal models, more efficient training techniques, and applications in scientific research. Large language models continue to evolve with improvements in reasoning capabilities and specialized domain knowledge.",
                metadata: { model: "anthropic/claude-3-opus" }
              },
              timestamp: "2025-03-15T10:31:45Z"
            },
            {
              step: 7,
              agent_id: 'agent-2',
              agent_name: 'Analyst',
              type: 'complete',
              timestamp: "2025-03-15T10:32:00Z"
            }
          ]
        }
      });
    }
  }
  
  // Mock POST responses
  if (method === 'post') {
    // Flow creation
    if (endpoint === '/flows') {
      const flowData = JSON.parse(config.data);
      return Promise.resolve({
        data: {
          flow_id: Math.random().toString(36).substring(2, 9),
          ...flowData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      });
    }
    
    // Flow execution
    if (endpoint === '/executions') {
      const executionData = JSON.parse(config.data);
      return Promise.resolve({
        data: {
          execution_id: Math.random().toString(36).substring(2, 9),
          status: 'pending',
          flow_id: executionData.flow_id,
          framework: executionData.framework || 'langgraph',
          input: executionData.input,
          started_at: new Date().toISOString(),
        }
      });
    }
  }
  
  // Mock PUT responses
  if (method === 'put' && endpoint.match(/^\/flows\/[a-zA-Z0-9-]+$/)) {
    const flowId = endpoint.split('/').pop();
    const flowData = JSON.parse(config.data);
    return Promise.resolve({
      data: {
        flow_id: flowId,
        ...flowData,
        updated_at: new Date().toISOString()
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
    getStats: () => api.get('/executions/stats/'),
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
  
  // Authentication helpers
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    logout: () => {
      localStorage.removeItem('nexusflow_api_key');
      return Promise.resolve();
    },
    isAuthenticated: () => Boolean(localStorage.getItem('nexusflow_api_key')),
    setApiKey: (apiKey) => {
      localStorage.setItem('nexusflow_api_key', apiKey);
    }
  },
  
  // Mock mode helpers for development
  mock: {
    enable: () => {
      localStorage.setItem('nexusflow_use_mock', 'true');
      window.location.reload();
    },
    disable: () => {
      localStorage.removeItem('nexusflow_use_mock');
      window.location.reload();
    },
    isEnabled: () => useMockApi || localStorage.getItem('nexusflow_use_mock') === 'true'
  }
};

export default apiService;
