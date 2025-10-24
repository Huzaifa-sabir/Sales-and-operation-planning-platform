import axiosInstance from './axios';
import type { LoginCredentials, LoginResponse, User } from '@/types';

export const authAPI = {
  // Login - Backend expects JSON with email/username and password
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response = await axiosInstance.post<{
        access_token: string;
        token_type: string;
        user: {
          _id: string;
          username: string;
          email: string;
          fullName: string;
          role: string;
          isActive: boolean;
          lastLogin?: string;
          createdAt?: string;
          updatedAt?: string;
        };
      }>('/auth/login', {
        email: credentials.email,  // Send as email
        password: credentials.password,
      });

      // Transform backend response to frontend format
      return {
        accessToken: response.data.access_token,
        tokenType: response.data.token_type,
        user: {
          _id: response.data.user._id,
          username: response.data.user.username,
          email: response.data.user.email,
          fullName: response.data.user.fullName,
          role: response.data.user.role as 'admin' | 'sales_rep',
          isActive: response.data.user.isActive,
          createdAt: response.data.user.createdAt || new Date().toISOString(),
          updatedAt: response.data.user.updatedAt || new Date().toISOString(),
        },
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Get current user
  me: async (): Promise<User> => {
    const response = await axiosInstance.get<{
      id: string;
      username: string;
      email: string;
      firstName: string;
      lastName: string;
      fullName: string;
      role: string;
      employeeId: string;
      isActive: boolean;
    }>('/auth/me');

    return {
      _id: response.data.id,
      username: response.data.username,
      email: response.data.email || response.data.username,
      fullName: response.data.fullName || `${response.data.firstName} ${response.data.lastName}`,
      role: response.data.role as 'admin' | 'sales_rep',
      isActive: response.data.isActive,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  // Logout
  logout: async (): Promise<void> => {
    await axiosInstance.post('/auth/logout');
  },

  // Refresh token (if implemented)
  refreshToken: async (): Promise<LoginResponse> => {
    const response = await axiosInstance.post<LoginResponse>('/auth/refresh');
    return response.data;
  },
};
