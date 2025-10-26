import axiosInstance from './axios';

export interface Report {
  id: string;
  reportType: string;
  format: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  fileName?: string;
  downloadUrl?: string;
  fileSize?: number;
  generatedBy: string;
  generatedAt?: string;
  expiresAt?: string;
  recordCount?: number;
  processingTime?: number;
  error?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GenerateReportParams {
  reportType: string;
  format?: 'excel' | 'pdf';
  cycleId?: string;
  customerId?: string;
  productId?: string;
  startDate?: string;
  endDate?: string;
  year?: number;
  month?: number;
  includeCharts?: boolean;
  includeRawData?: boolean;
}

export interface EmailReportParams {
  reportId: string;
  recipients: string[];
  subject?: string;
  message?: string;
}

export interface ReportGenerationResponse {
  success: boolean;
  message: string;
  reportId: string;
  status: string;
  estimatedTime?: number;
}

export const reportsAPI = {
  // Instant download - generates and downloads report immediately (no polling)
  generateInstant: async (params: GenerateReportParams): Promise<Blob> => {
    const response = await axiosInstance.post('/reports/generate-instant', params, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Unified generate report method (async)
  generate: async (params: GenerateReportParams): Promise<ReportGenerationResponse> => {
    const response = await axiosInstance.post<ReportGenerationResponse>('/reports/generate', params);
    return response.data;
  },

  // Generate forecast summary report
  generateForecastSummary: async (cycleId: string): Promise<ReportGenerationResponse> => {
    return reportsAPI.generate({
      reportType: 'forecast_vs_actual',
      format: 'excel',
      cycleId
    });
  },

  // Generate sales vs forecast comparison
  generateSalesComparison: async (cycleId: string): Promise<ReportGenerationResponse> => {
    return reportsAPI.generate({
      reportType: 'sales_summary',
      format: 'excel',
      cycleId
    });
  },

  // Generate customer performance report
  generateCustomerPerformance: async (cycleId: string, customerId?: string): Promise<ReportGenerationResponse> => {
    return reportsAPI.generate({
      reportType: 'customer_performance',
      format: 'excel',
      cycleId,
      customerId
    });
  },

  // Generate product performance report
  generateProductPerformance: async (cycleId: string, productId?: string): Promise<ReportGenerationResponse> => {
    return reportsAPI.generate({
      reportType: 'product_analysis',
      format: 'excel',
      cycleId,
      productId
    });
  },

  // Generate territory performance report
  generateTerritoryPerformance: async (cycleId: string): Promise<ReportGenerationResponse> => {
    return reportsAPI.generate({
      reportType: 'monthly_dashboard',
      format: 'excel',
      cycleId
    });
  },

  // Get report status (for polling)
  getStatus: async (reportId: string): Promise<Report> => {
    const response = await axiosInstance.get<Report>(`/reports/${reportId}`);
    return response.data;
  },

  // Download report by ID
  download: async (reportId: string): Promise<Blob> => {
    const response = await axiosInstance.get(`/reports/${reportId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Email report
  email: async (params: EmailReportParams): Promise<{ message: string }> => {
    const response = await axiosInstance.post('/reports/email', params);
    return response.data;
  },

  // List reports with pagination
  list: async (params?: {
    skip?: number;
    limit?: number;
    reportType?: string;
    status?: string;
  }): Promise<{ total: number; reports: Report[] }> => {
    const response = await axiosInstance.get('/reports', { params });
    return response.data;
  },

  // Delete report
  delete: async (reportId: string): Promise<void> => {
    await axiosInstance.delete(`/reports/${reportId}`);
  },
};
