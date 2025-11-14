import axiosInstance from './axios';

export interface MonthlyForecast {
  year: number;
  month: number; // 1-12
  monthLabel: string; // YYYY-MM
  quantity: number;
  unitPrice?: number;
  revenue?: number;
  notes?: string;
  isHistorical?: boolean;
  isCurrent?: boolean;
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

  exportAll: async (cycleId: string): Promise<Blob> => {
    const res = await axiosInstance.get(`/forecasts/cycle/${cycleId}/export`, { responseType: 'blob' });
    return res.data;
  },

  bulkUpload: async (cycleId: string, file: File): Promise<{ success: boolean; message: string; imported: number; failed: number; errors: string[] }> => {
    const form = new FormData();
    form.append('file', file);
    const res = await axiosInstance.post(`/forecasts/bulk-import?cycle_id=${encodeURIComponent(cycleId)}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  bulkCreate: async (cycleId: string, customerId: string, forecasts: Array<{
    productId: string;
    monthlyForecasts: MonthlyForecast[];
    useCustomerPrice?: boolean;
    overridePrice?: number;
    notes?: string;
  }>): Promise<{ success: boolean; message: string; forecasts: Forecast[]; created: number; updated: number }> => {
    const res = await axiosInstance.post('/forecasts/bulk', {
      cycleId,
      customerId,
      forecasts
    });
    return res.data;
  },
};
