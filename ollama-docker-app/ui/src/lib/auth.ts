import axios from 'axios';

// Use Vite environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const ANON_KEY = import.meta.env.VITE_ANON_KEY || '';

// Create an axios instance for SelfDB API
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor to include auth token and anon key
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (config.headers && ANON_KEY) {
      config.headers['apikey'] = ANON_KEY;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Types
export interface LoginResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
  is_superuser: boolean;
  email: string;
  user_id: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name?: string;
  created_at: string;
}

// Login user
export const loginUser = async (email: string, password: string): Promise<LoginResponse> => {
  const data = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
  const response = await api.post('/auth/login', data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};// Register user
export const registerUser = async (email: string, password: string, fullName?: string): Promise<User> => {
  const response = await api.post('/auth/register', {
    email,
    password,
    full_name: fullName,
    is_active: true,
    is_superuser: false,
  });
  return response.data;
};

// Get current user
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/users/me');
  return response.data;
};