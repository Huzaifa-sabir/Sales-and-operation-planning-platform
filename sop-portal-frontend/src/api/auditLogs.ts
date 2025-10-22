import axiosInstance from './axios';

export interface AuditLog {
  _id: string;
  action: string;
  userId?: string;
  userName?: string;
  entityType?: string;
  entityId?: string;
  changes?: Record<string, any>;
  oldValues?: Record<string, any>;
  newValues?: Record<string, any>;
  ipAddress?: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  timestamp: string;
}

export interface AuditStatistics {
  totalLogs: number;
  byAction: Record<string, number>;
  bySeverity: Record<string, number>;
  mostActiveUsers: Array<{
    userId: string;
    userName: string;
    count: number;
  }>;
}

export const auditLogsAPI = {
  // List audit logs with filters (admin only)
  list: async (params?: {
    skip?: number;
    limit?: number;
    userId?: string;
    action?: string;
    entityType?: string;
    severity?: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
    startDate?: string;
    endDate?: string;
  }): Promise<{ total: number; logs: AuditLog[] }> => {
    const response = await axiosInstance.get('/audit-logs', { params });
    return response.data;
  },

  // Get my activity logs
  getMyActivity: async (days: number = 30): Promise<AuditLog[]> => {
    const response = await axiosInstance.get<AuditLog[]>('/audit-logs/my-activity', {
      params: { days }
    });
    return response.data;
  },

  // Get entity history
  getEntityHistory: async (entityType: string, entityId: string): Promise<AuditLog[]> => {
    const response = await axiosInstance.get<AuditLog[]>(`/audit-logs/entity/${entityType}/${entityId}`);
    return response.data;
  },

  // Get critical events (admin only)
  getCriticalEvents: async (hours: number = 24): Promise<AuditLog[]> => {
    const response = await axiosInstance.get<AuditLog[]>('/audit-logs/critical-events', {
      params: { hours }
    });
    return response.data;
  },

  // Get audit statistics (admin only)
  getStatistics: async (startDate?: string, endDate?: string): Promise<AuditStatistics> => {
    const response = await axiosInstance.get<AuditStatistics>('/audit-logs/statistics', {
      params: { startDate, endDate }
    });
    return response.data;
  },
};
