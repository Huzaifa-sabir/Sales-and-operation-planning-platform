import axiosInstance from './axios';
import type { SOPForecast, PaginatedResponse } from '@/types';

export type ForecastMonthData = {
  forecastMonth: string;  // YYYY-MM format
  quantity: number;
  unitPrice: number;
}

export type ForecastCreate = {
  cycleId: string;
  customerId: string;
  productId: string;
  forecasts: ForecastMonthData[];
}

export type ForecastUpdate = {
  forecasts: ForecastMonthData[];
}

export const forecastsAPI = {
  // List forecasts with pagination and filters
  list: async (params?: {
    skip?: number;
    limit?: number;
    cycleId?: string;
    salesRepId?: string;
    customerId?: string;
    productId?: string;
    status?: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
  }): Promise<PaginatedResponse<SOPForecast>> => {
    const response = await axiosInstance.get<PaginatedResponse<SOPForecast>>('/forecasts', { params });
    return response.data;
  },

  // Get my forecasts for a cycle
  getMy: async (cycleId: string): Promise<SOPForecast[]> => {
    const response = await axiosInstance.get<SOPForecast[]>(`/forecasts/my/${cycleId}`);
    return response.data;
  },

  // Get forecast by ID
  get: async (id: string): Promise<SOPForecast> => {
    const response = await axiosInstance.get<SOPForecast>(`/forecasts/${id}`);
    return response.data;
  },

  // Create new forecast
  create: async (forecastData: ForecastCreate): Promise<SOPForecast> => {
    const response = await axiosInstance.post<SOPForecast>('/forecasts', forecastData);
    return response.data;
  },

  // Update forecast
  update: async (id: string, forecastData: ForecastUpdate): Promise<SOPForecast> => {
    const response = await axiosInstance.put<SOPForecast>(`/forecasts/${id}`, forecastData);
    return response.data;
  },

  // Delete forecast
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/forecasts/${id}`);
  },

  // Submit forecast
  submit: async (id: string): Promise<SOPForecast> => {
    const response = await axiosInstance.post<SOPForecast>(`/forecasts/${id}/submit`);
    return response.data;
  },

  // Approve forecast (manager/admin only)
  approve: async (id: string, comment?: string): Promise<SOPForecast> => {
    const response = await axiosInstance.post<SOPForecast>(`/forecasts/${id}/approve`, { comment });
    return response.data;
  },

  // Reject forecast (manager/admin only)
  reject: async (id: string, comment: string): Promise<SOPForecast> => {
    const response = await axiosInstance.post<SOPForecast>(`/forecasts/${id}/reject`, { comment });
    return response.data;
  },

  // Bulk submit forecasts for a cycle
  bulkSubmit: async (cycleId: string): Promise<{ message: string; count: number }> => {
    const response = await axiosInstance.post(`/forecasts/bulk-submit/${cycleId}`);
    return response.data;
  },

  // Download forecast template
  downloadTemplate: async (cycleId: string): Promise<Blob> => {
    const response = await axiosInstance.get(`/forecasts/cycle/${cycleId}/template`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Bulk import forecasts from Excel
  bulkImport: async (cycleId: string, file: File): Promise<{ message: string; imported: number; failed: number; errors: string[] }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosInstance.post(`/forecasts/bulk-import?cycle_id=${cycleId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Export forecasts to Excel
  exportForecasts: async (cycleId: string): Promise<Blob> => {
    const response = await axiosInstance.get(`/forecasts/cycle/${cycleId}/export`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
