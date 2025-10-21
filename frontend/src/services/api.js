import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const login = (username, password) => {
  return api.post('/auth/login', { username, password });
};

// Metrics
export const getMetrics = (params = {}) => {
  return api.get('/metrics', { params });
};

export const getCurrentMetrics = () => {
  return api.get('/metrics/current');
};

export const submitMetrics = (data) => {
  return api.post('/metrics', data);
};

export const getAggregatedMetrics = (interval = 'hour') => {
  return api.get('/metrics/aggregated', { params: { interval } });
};

// Predictions
export const getPredictions = (limit = 50) => {
  return api.get('/predictions', { params: { limit } });
};

export const generatePredictions = (steps = 12) => {
  return api.post('/predictions/generate', null, { params: { steps } });
};

export const trainModel = (data = {}) => {
  return api.post('/predictions/train', data);
};

// Resources
export const getResources = () => {
  return api.get('/resources');
};

export const getRecommendations = () => {
  return api.get('/resources/recommendations');
};

export const allocateResources = (data = {}) => {
  return api.post('/resources/allocate', data);
};

// Dashboard
export const getDashboardStats = () => {
  return api.get('/dashboard/stats');
};

export const getHistory = (days = 7) => {
  return api.get('/dashboard/history', { params: { days } });
};

// System
export const getSystemInfo = () => {
  return api.get('/system/info');
};

export const healthCheck = () => {
  return api.get('/health');
};

export default api;
