import axiosInstance from './axios';
import type { Customer, CustomerFormData, TableFilters } from '@/types';

export const customersAPI = {
  // Get all customers with filters
  getAll: async (filters?: TableFilters): Promise<{
    customers: Customer[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  }> => {
    const params = new URLSearchParams();

    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.search) params.append('search', filters.search);
    if (filters?.salesRepId) params.append('sales_rep_id', filters.salesRepId as string);
    if (filters?.isActive !== undefined) params.append('is_active', filters.isActive.toString());

    const response = await axiosInstance.get<{
      customers: Customer[];
      total: number;
      page: number;
      pageSize: number;
      totalPages: number;
      hasNext: boolean;
      hasPrev: boolean;
    }>(`/customers?${params.toString()}`);
    return response.data;
  },

  // Get single customer
  getById: async (id: string): Promise<Customer> => {
    const response = await axiosInstance.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  // Create customer
  create: async (data: CustomerFormData): Promise<Customer> => {
    const response = await axiosInstance.post<Customer>('/customers', data);
    return response.data;
  },

  // Update customer
  update: async (id: string, data: Partial<CustomerFormData>): Promise<Customer> => {
    const response = await axiosInstance.put<Customer>(`/customers/${id}`, data);
    return response.data;
  },

  // Delete customer
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/customers/${id}`);
  },

  // Import from Excel
  importExcel: async (file: File): Promise<{ total: number; successful: number; failed: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosInstance.post('/excel/import/customers', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Export to Excel
  exportExcel: async (): Promise<Blob> => {
    const response = await axiosInstance.get('/excel/export/customers', {
      responseType: 'blob',
    });
    return response.data;
  },

  // Download Excel template
  downloadTemplate: async (): Promise<Blob> => {
    const response = await axiosInstance.get('/excel/templates/customers', {
      responseType: 'blob',
    });
    return response.data;
  },
};
