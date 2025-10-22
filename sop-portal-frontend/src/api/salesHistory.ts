import axiosInstance from './axios';
import type { SalesHistory, PaginatedResponse } from '@/types';

export interface SalesHistoryCreate {
  customerId: string;
  productId: string;
  year: number;
  month: number;
  quantity: number;
  unitPrice: number;
  invoiceNumber?: string;
  deliveryDate?: string;
}

export interface SalesSummary {
  totalSales: number;
  totalQuantity: number;
  avgUnitPrice: number;
  periodStart: string;
  periodEnd: string;
  byMonth: Array<{
    yearMonth: string;
    sales: number;
    quantity: number;
  }>;
}

export const salesHistoryAPI = {
  // List sales history with pagination and filters
  list: async (params?: {
    skip?: number;
    limit?: number;
    customerId?: string;
    productId?: string;
    salesRepId?: string;
    year?: number;
    month?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<PaginatedResponse<SalesHistory>> => {
    const response = await axiosInstance.get<PaginatedResponse<SalesHistory>>('/sales-history', { params });
    return response.data;
  },

  // Get sales history by ID
  get: async (id: string): Promise<SalesHistory> => {
    const response = await axiosInstance.get<SalesHistory>(`/sales-history/${id}`);
    return response.data;
  },

  // Get sales summary
  getSummary: async (params: {
    customerId?: string;
    productId?: string;
    salesRepId?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<SalesSummary> => {
    const response = await axiosInstance.get<SalesSummary>('/sales-history/summary', { params });
    return response.data;
  },

  // Create sales history record (admin only)
  create: async (salesData: SalesHistoryCreate): Promise<SalesHistory> => {
    const response = await axiosInstance.post<SalesHistory>('/sales-history', salesData);
    return response.data;
  },

  // Update sales history record (admin only)
  update: async (id: string, salesData: Partial<SalesHistoryCreate>): Promise<SalesHistory> => {
    const response = await axiosInstance.put<SalesHistory>(`/sales-history/${id}`, salesData);
    return response.data;
  },

  // Delete sales history record (admin only)
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/sales-history/${id}`);
  },

  // Export sales history to Excel
  exportExcel: async (params?: {
    customerId?: string;
    productId?: string;
    year?: number;
    month?: number;
    limit?: number;
  }): Promise<Blob> => {
    const response = await axiosInstance.get(`/excel/export/sales-history`, {
      params,
      responseType: 'blob',
    });
    return response.data as Blob;
  },

  // Import sales history from Excel (admin only)
  importExcel: async (file: File): Promise<{ message: string; imported: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosInstance.post('/sales-history/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
};
