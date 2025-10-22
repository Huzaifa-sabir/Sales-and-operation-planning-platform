import axiosInstance from './axios';

export interface PricingMatrix {
  _id: string;
  customerId: string;
  customerName: string;
  productId: string;
  productCode: string;
  productDescription: string;
  unitPrice: number;
  effectiveDate: string;
  endDate?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PricingMatrixCreate {
  customerId: string;
  productId: string;
  unitPrice: number;
  effectiveDate: string;
  endDate?: string;
}

export interface PricingMatrixUpdate {
  unitPrice?: number;
  effectiveDate?: string;
  endDate?: string;
  isActive?: boolean;
}

export const matrixAPI = {
  // List pricing matrix with pagination and filters
  list: async (params?: {
    skip?: number;
    limit?: number;
    customerId?: string;
    productId?: string;
    isActive?: boolean;
  }): Promise<{ total: number; data: PricingMatrix[] }> => {
    const response = await axiosInstance.get('/matrix', { params });
    return response.data;
  },

  // Get pricing matrix by ID
  get: async (id: string): Promise<PricingMatrix> => {
    const response = await axiosInstance.get<PricingMatrix>(`/matrix/${id}`);
    return response.data;
  },

  // Get price for customer-product combination
  getPrice: async (customerId: string, productId: string): Promise<PricingMatrix | null> => {
    const response = await axiosInstance.get<PricingMatrix | null>('/matrix/price', {
      params: { customerId, productId }
    });
    return response.data;
  },

  // Create pricing matrix entry (admin only)
  create: async (matrixData: PricingMatrixCreate): Promise<PricingMatrix> => {
    const response = await axiosInstance.post<PricingMatrix>('/matrix', matrixData);
    return response.data;
  },

  // Update pricing matrix entry (admin only)
  update: async (id: string, matrixData: PricingMatrixUpdate): Promise<PricingMatrix> => {
    const response = await axiosInstance.put<PricingMatrix>(`/matrix/${id}`, matrixData);
    return response.data;
  },

  // Delete pricing matrix entry (admin only)
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/matrix/${id}`);
  },

  // Import pricing matrix from Excel (admin only)
  importExcel: async (file: File): Promise<{ message: string; imported: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosInstance.post('/excel/import/matrix', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Download Excel template
  downloadTemplate: async (): Promise<Blob> => {
    const response = await axiosInstance.get('/excel/templates/matrix', {
      responseType: 'blob',
    });
    return response.data;
  },
};
