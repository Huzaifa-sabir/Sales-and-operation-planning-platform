import axiosInstance from './axios';
import type { User } from '@/types';

export interface UserCreate {
  username: string;
  email: string;
  fullName: string;
  role: 'admin' | 'sales_rep';
}

export interface UserUpdate {
  username?: string;
  email?: string;
  fullName?: string;
  role?: 'admin' | 'sales_rep';
}

export interface UserCreateResponse {
  user: User;
  generatedPassword: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

export const usersAPI = {
  // List users with pagination and filters
  list: async (params?: {
    page?: number;
    pageSize?: number;
    role?: string;
    isActive?: boolean;
    search?: string;
  }): Promise<UserListResponse> => {
    const response = await axiosInstance.get<UserListResponse>('/users', { params });
    return response.data;
  },

  // Get user by ID
  get: async (id: string): Promise<User> => {
    const response = await axiosInstance.get<User>(`/users/${id}`);
    return response.data;
  },

  // Get current user (me)
  me: async (): Promise<User> => {
    const response = await axiosInstance.get<User>('/auth/me');
    return response.data;
  },

  // Create new user (admin only)
  create: async (userData: UserCreate): Promise<UserCreateResponse> => {
    const response = await axiosInstance.post<UserCreateResponse>('/users', userData);
    return response.data;
  },

  // Update user (admin only)
  update: async (id: string, userData: UserUpdate): Promise<User> => {
    const response = await axiosInstance.put<User>(`/users/${id}`, userData);
    return response.data;
  },

  // Toggle user status (admin only)
  toggleStatus: async (id: string): Promise<User> => {
    const response = await axiosInstance.patch<User>(`/users/${id}/toggle-status`);
    return response.data;
  },

  // Delete user (admin only)
  delete: async (id: string): Promise<MessageResponse> => {
    const response = await axiosInstance.delete<MessageResponse>(`/users/${id}`);
    return response.data;
  },

  // Request password reset (public endpoint)
  requestPasswordReset: async (email: string): Promise<MessageResponse> => {
    const response = await axiosInstance.post<MessageResponse>('/users/password-reset/request', { email });
    return response.data;
  },

  // Confirm password reset with token (public endpoint)
  confirmPasswordReset: async (token: string, newPassword: string): Promise<MessageResponse> => {
    const response = await axiosInstance.post<MessageResponse>('/users/password-reset/confirm', {
      token,
      newPassword
    });
    return response.data;
  },
};
