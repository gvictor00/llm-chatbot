import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send a chat message
  sendMessage: async (message, options = {}) => {
    const payload = {
      message,
      model: options.model || 'gpt-4o',
      agent_name: options.agentName || 'llm-chatbot-ui',
      max_tokens: options.maxTokens || 1000,
      temperature: options.temperature || 0.7,
      top_k_documents: options.topK || 3,
    };

    const response = await api.post('/chat', payload);
    return response.data;
  },

  // Check API health
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Load documents
  loadDocuments: async () => {
    const response = await api.get('/load_documents');
    return response.data;
  },

  // Get RAG statistics
  getRagStats: async () => {
    const response = await api.get('/rag/stats');
    return response.data;
  },

  // Get available models
  getModels: async () => {
    const response = await api.get('/models');
    return response.data;
  },

  // Get document statistics
  getDocumentStats: async () => {
    const response = await api.get('/documents/stats');
    return response.data;
  },
};

export default api;
