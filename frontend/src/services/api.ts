import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Disable credentials for now to avoid CORS issues
  timeout: 10000, // 10 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Create a new config object to avoid mutating the original
    const newConfig = { ...config };
    
    // Ensure headers exist
    newConfig.headers = newConfig.headers || {};
    
    // Add auth token if available
    // const token = localStorage.getItem('token');
    // if (token) {
    //   newConfig.headers.Authorization = `Bearer ${token}`;
    // }
    
    // Add cache control headers for GET requests
    if (newConfig.method?.toLowerCase() === 'get') {
      newConfig.headers['Cache-Control'] = 'no-cache';
      newConfig.headers['Pragma'] = 'no-cache';
    }
    
    return newConfig;
  },
  (error: AxiosError) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Handle successful responses
    return response;
  },
  async (error: AxiosError) => {
    // Handle errors globally
    const originalRequest = error.config;
    
    // Log error details
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      url: originalRequest?.url,
      method: originalRequest?.method,
      data: error.response?.data,
    });
    
    // Handle specific status codes
    if (error.response) {
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        // Handle unauthorized access (e.g., redirect to login)
        // window.location.href = '/login';
        console.warn('Unauthorized access - please log in');
      }
    }
    
    // Return a more informative error
    return Promise.reject({
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      isAxiosError: true,
    });
  }
);

export default apiClient;
