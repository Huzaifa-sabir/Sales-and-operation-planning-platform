import axiosInstance from './axios';
import type { LoginCredentials, LoginResponse, User } from '@/types';

export const authAPI = {
  // Login - Backend expects JSON with username and password
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response = await axiosInstance.post<{
        access_token: string;
        token_type: string;
        expires_in: number;
        user: {
          id: string;
          username: string;
          email: string;
          firstName: string;
          lastName: string;
          fullName: string;
          role: string;
          employeeId: string;
          isActive: boolean;
        };
      }>('/auth/login', {
        username: credentials.email, // Send as username (backend will detect if it's an email)
        password: credentials.password,
      });

      // Transform backend response to frontend format
      return {
        accessToken: response.data.access_token,
        tokenType: response.data.token_type,
        user: {
          _id: response.data.user.id,
          username: response.data.user.username,
          email: response.data.user.email || response.data.user.username,
          fullName: response.data.user.fullName || `${response.data.user.firstName} ${response.data.user.lastName}`,
          role: response.data.user.role as 'admin' | 'sales_rep',
          isActive: response.data.user.isActive,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
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
