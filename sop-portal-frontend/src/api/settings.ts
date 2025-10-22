import axiosInstance from './axios';

export interface Setting {
  id: string;
  key: string;
  value: any;
  category: 'general' | 'notifications' | 'sop_cycle' | 'email' | 'security' | 'reports' | 'system';
  label: string;
  description?: string;
  dataType: 'string' | 'number' | 'boolean' | 'json';
  isPublic: boolean;
  isEditable: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface SettingUpdate {
  value: any;
  label?: string;
  description?: string;
}

export interface PublicSettings {
  [key: string]: any;
}

export const settingsAPI = {
  // Get public settings (no auth required)
  getPublic: async (): Promise<PublicSettings> => {
    const response = await axiosInstance.get<PublicSettings>('/settings/public');
    return response.data;
  },

  // List all settings (admin only)
  list: async (params?: {
    category?: string;
    isPublic?: boolean;
  }): Promise<{ total: number; settings: Setting[] }> => {
    const response = await axiosInstance.get('/settings', { params });
    return response.data;
  },

  // Get setting by key
  get: async (key: string): Promise<Setting> => {
    const response = await axiosInstance.get<Setting>(`/settings/${key}`);
    return response.data;
  },

  // Update setting (admin only)
  update: async (key: string, data: SettingUpdate): Promise<Setting> => {
    const response = await axiosInstance.put<Setting>(`/settings/${key}`, data);
    return response.data;
  },

  // Create setting (admin only)
  create: async (settingData: Omit<Setting, '_id' | 'createdAt' | 'updatedAt'>): Promise<Setting> => {
    const response = await axiosInstance.post<Setting>('/settings', settingData);
    return response.data;
  },

  // Delete setting (admin only)
  delete: async (key: string): Promise<void> => {
    await axiosInstance.delete(`/settings/${key}`);
  },
};
