import axiosInstance from './axios';
import type { SOPCycle, PaginatedResponse } from '@/types';

export interface CycleCreate {
  cycleName: string;
  startDate: string;  // ISO date string
  endDate: string;    // ISO date string
}

export interface CycleUpdate {
  cycleName?: string;
  startDate?: string;
  endDate?: string;
}

export interface CycleStats {
  totalSalesReps: number;
  submittedForecasts: number;
  pendingForecasts: number;
  totalForecastAmount: number;
  completionPercentage: number;
}

export const cyclesAPI = {
  // List cycles with pagination and filters
  list: async (params?: {
    skip?: number;
    limit?: number;
    status?: 'DRAFT' | 'OPEN' | 'CLOSED';
    year?: number;
  }): Promise<PaginatedResponse<SOPCycle>> => {
    const response = await axiosInstance.get<PaginatedResponse<SOPCycle>>('/sop/cycles', { params });
    return response.data;
  },

  // Get cycle by ID
  get: async (id: string): Promise<SOPCycle> => {
    const response = await axiosInstance.get<SOPCycle>(`/sop/cycles/${id}`);
    return response.data;
  },

  // Get current active cycle
  getCurrent: async (): Promise<SOPCycle | null> => {
    const response = await axiosInstance.get<SOPCycle | null>('/sop/cycles/active');
    return response.data;
  },

  // Create new cycle (admin only)
  create: async (cycleData: CycleCreate): Promise<SOPCycle> => {
    const response = await axiosInstance.post<SOPCycle>('/sop/cycles', cycleData);
    return response.data;
  },

  // Update cycle (admin only)
  update: async (id: string, cycleData: CycleUpdate): Promise<SOPCycle> => {
    const response = await axiosInstance.put<SOPCycle>(`/sop/cycles/${id}`, cycleData);
    return response.data;
  },

  // Delete cycle (admin only)
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/sop/cycles/${id}`);
  },

  // Change cycle status (admin only)
  changeStatus: async (id: string, status: 'DRAFT' | 'OPEN' | 'CLOSED'): Promise<SOPCycle> => {
    const response = await axiosInstance.put<SOPCycle>(`/sop/cycles/${id}/status`, { status });
    return response.data;
  },

  // Get cycle statistics
  getStats: async (id: string): Promise<CycleStats> => {
    const response = await axiosInstance.get<CycleStats>(`/sop/cycles/${id}/stats`);
    return response.data;
  },
};
