import axiosInstance from './axios';

export interface MonthlyForecast {
  month: string; // YYYY-MM
  quantity: number;
}

export interface Forecast {
  _id: string;
  cycleId: string;
  customerId: string;
  productId: string;
  salesRepId: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
  monthlyForecasts: MonthlyForecast[];
  useCustomerPrice: boolean;
  overridePrice?: number;
  totalQuantity: number;
  totalRevenue: number;
  version: number;
  previousVersionId?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  submittedAt?: string;
}

export interface ForecastCreate {
  cycleId: string;
  customerId: string;
  productId: string;
  monthlyForecasts: MonthlyForecast[];
  useCustomerPrice: boolean;
  overridePrice?: number;
  notes?: string;
}

export interface ForecastUpdate {
  monthlyForecasts?: MonthlyForecast[];
  useCustomerPrice?: boolean;
  overridePrice?: number;
  notes?: string;
}

export const forecastsAPI = {
  list: async (params: {
    page?: number;
    pageSize?: number;
    cycleId?: string;
    customerId?: string;
    productId?: string;
    status?: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
  }): Promise<{ forecasts: Forecast[]; total: number; page: number; pageSize: number; totalPages: number; hasNext: boolean; hasPrev: boolean }> => {
    const res = await axiosInstance.get('/forecasts', { params });
    return res.data;
  },

  get: async (id: string): Promise<Forecast> => {
    const res = await axiosInstance.get(`/forecasts/${id}`);
    return res.data;
  },

  create: async (data: ForecastCreate): Promise<Forecast> => {
    const res = await axiosInstance.post('/forecasts', data);
    return res.data;
  },

  update: async (id: string, data: ForecastUpdate): Promise<Forecast> => {
    const res = await axiosInstance.put(`/forecasts/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/forecasts/${id}`);
  },

  submit: async (id: string): Promise<{ success: boolean; message: string; forecast: Forecast }> => {
    const res = await axiosInstance.post(`/forecasts/${id}/submit`);
    return res.data;
  },

  template: async (cycleId: string): Promise<Blob> => {
    const res = await axiosInstance.get(`/forecasts/cycle/${cycleId}/template`, { responseType: 'blob' });
    return res.data;
  },

  export: async (cycleId: string): Promise<Blob> => {
    const res = await axiosInstance.get(`/forecasts/cycle/${cycleId}/export`, { responseType: 'blob' });
    return res.data;
  },

  bulkUpload: async (cycleId: string, file: File): Promise<{ success: boolean; message: string; imported: number; failed: number; errors: string[] }>{
    const form = new FormData();
    form.append('file', file);
    const res = await axiosInstance.post(`/forecasts/bulk-import?cycle_id=${encodeURIComponent(cycleId)}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

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
