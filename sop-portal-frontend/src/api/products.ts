import axiosInstance from './axios';
import type { Product, ProductFormData, TableFilters } from '@/types';

export const productsAPI = {
  // Get all products with filters
  getAll: async (filters?: TableFilters): Promise<{
    products: Product[];
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
    if (filters?.groupCode) params.append('group_code', filters.groupCode as string);
    if (filters?.location) params.append('location', filters.location as string);
    if (filters?.isActive !== undefined) params.append('isActive', filters.isActive.toString());

    const response = await axiosInstance.get<{
      products: Product[];
      total: number;
      page: number;
      pageSize: number;
      totalPages: number;
      hasNext: boolean;
      hasPrev: boolean;
    }>(`/products?${params.toString()}`);
    return response.data;
  },

  // Get products by customer (filtered by product-customer matrix)
  getByCustomer: async (customerId: string, filters?: TableFilters): Promise<{
    products: Product[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  }> => {
    const params = new URLSearchParams();
    params.append('customerId', customerId); // Make sure customerId is passed correctly

    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString()); // Backend accepts both limit and pageSize
    if (filters?.search) params.append('search', filters.search);
    if (filters?.groupCode) params.append('group_code', filters.groupCode as string);
    if (filters?.location) params.append('location', filters.location as string);
    if (filters?.isActive !== undefined) params.append('isActive', filters.isActive.toString());

    console.log(`[productsAPI.getByCustomer] Calling API with customerId=${customerId}, params=${params.toString()}`);
    
    const response = await axiosInstance.get<{
      products: Product[];
      total: number;
      page: number;
      pageSize: number;
      totalPages: number;
      hasNext: boolean;
      hasPrev: boolean;
    }>(`/products?${params.toString()}`);
    
    console.log(`[productsAPI.getByCustomer] Received ${response.data.products.length} products for customer ${customerId}`);
    return response.data;
  },

  // Get single product
  getById: async (id: string): Promise<Product> => {
    const response = await axiosInstance.get<Product>(`/products/${id}`);
    return response.data;
  },

  // Create product
  create: async (data: ProductFormData): Promise<Product> => {
    const response = await axiosInstance.post<Product>('/products', data);
    return response.data;
  },

  // Update product
  update: async (id: string, data: Partial<ProductFormData>): Promise<Product> => {
    const response = await axiosInstance.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  // Delete product
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/products/${id}`);
  },

  // Import from Excel
  importExcel: async (file: File): Promise<{ total: number; successful: number; failed: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosInstance.post('/excel/import/products', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Export to Excel
  exportExcel: async (): Promise<Blob> => {
    const response = await axiosInstance.get('/excel/export/products', {
      responseType: 'blob',
    });
    return response.data;
  },

  // Download Excel template
  downloadTemplate: async (): Promise<Blob> => {
    const response = await axiosInstance.get('/excel/templates/products', {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get statistics
  getStatistics: async (): Promise<{
    total: number;
    active: number;
    inactive: number;
    groups: number;
  }> => {
    const response = await axiosInstance.get('/products/statistics');
    return response.data;
  },
};
