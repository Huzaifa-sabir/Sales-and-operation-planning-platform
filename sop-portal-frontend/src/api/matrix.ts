import axiosInstance from './axios';

export interface ProductCustomerMatrix {
  _id: string;
  customerId: string;
  productId: string;
  customerPrice?: number;
  minimumOrderQty?: number;
  maximumOrderQty?: number;
  leadTimeDays?: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface MatrixCreate {
  customerId: string;
  productId: string;
  customerPrice?: number;
  minimumOrderQty?: number;
  maximumOrderQty?: number;
  leadTimeDays?: number;
}

export interface MatrixUpdate {
  isActive?: boolean;
  customerPrice?: number;
  minimumOrderQty?: number;
  maximumOrderQty?: number;
  leadTimeDays?: number;
}

export interface MatrixListResponse {
  entries: ProductCustomerMatrix[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export const matrixAPI = {
  // List all matrix entries
  list: async (params?: {
    page?: number;
    pageSize?: number;
    customerId?: string;
    productId?: string;
    isActive?: boolean;
  }): Promise<MatrixListResponse> => {
    const response = await axiosInstance.get<MatrixListResponse>('/matrix', { params });
    return response.data;
  },

  // Get products for a customer
  getByCustomer: async (customerId: string): Promise<ProductCustomerMatrix[]> => {
    const response = await axiosInstance.get<MatrixListResponse>('/matrix', {
      params: { customerId, page: 1, pageSize: 10000 }
    });
    return response.data.entries;
  },

  // Get customers for a product
  getByProduct: async (productId: string): Promise<ProductCustomerMatrix[]> => {
    const response = await axiosInstance.get<MatrixListResponse>('/matrix', {
      params: { productId, page: 1, pageSize: 10000 }
    });
    return response.data.entries;
  },

  // Create single entry
  create: async (data: MatrixCreate): Promise<ProductCustomerMatrix> => {
    const response = await axiosInstance.post<ProductCustomerMatrix>('/matrix', data);
    return response.data;
  },

  // Bulk create entries
  bulkCreate: async (entries: MatrixCreate[]): Promise<{
    success: boolean;
    message: string;
    created: ProductCustomerMatrix[];
  }> => {
    const response = await axiosInstance.post<{
      created: ProductCustomerMatrix[];
      failed: any[];
      totalCreated: number;
      totalFailed: number;
    }>('/matrix/bulk', { entries });
    return {
      success: response.data.totalFailed === 0,
      message: `Created ${response.data.totalCreated} entries`,
      created: response.data.created
    };
  },

  // Update entry
  update: async (id: string, data: MatrixUpdate): Promise<ProductCustomerMatrix> => {
    const response = await axiosInstance.put<ProductCustomerMatrix>(`/matrix/${id}`, data);
    return response.data;
  },

  // Delete entry
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/matrix/${id}`);
  },
};
