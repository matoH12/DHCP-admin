import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  User,
  UserCreate,
  UserUpdate,
  IPRange,
  IPRangeCreate,
  IPRangeStats,
  Device,
  DeviceCreate,
  DeviceUpdate,
  DHCPConfig,
  OverviewStatistics,
  DevicesByRangeStats,
  RecentDevice,
  SyslogMessage,
  SyslogStats,
  Setting,
  SettingUpdate,
  DHCPStatus,
  DHCPActivateResponse,
  ActivityTimelineResponse,
  DHCPEventsResponse,
  TopActiveDevicesResponse
} from '../types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 errors
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== Authentication ==========
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
    localStorage.removeItem('access_token');
  }

  // ========== IP Ranges ==========
  async getRanges(): Promise<IPRange[]> {
    const response = await this.api.get<IPRange[]>('/ranges/');
    return response.data;
  }

  async getRange(id: number): Promise<IPRange> {
    const response = await this.api.get<IPRange>(`/ranges/${id}`);
    return response.data;
  }

  async createRange(data: IPRangeCreate): Promise<IPRange> {
    const response = await this.api.post<IPRange>('/ranges/', data);
    return response.data;
  }

  async updateRange(id: number, data: Partial<IPRangeCreate>): Promise<IPRange> {
    const response = await this.api.put<IPRange>(`/ranges/${id}`, data);
    return response.data;
  }

  async deleteRange(id: number): Promise<void> {
    await this.api.delete(`/ranges/${id}`);
  }

  async getRangeStats(id: number): Promise<IPRangeStats> {
    const response = await this.api.get<IPRangeStats>(`/ranges/${id}/stats`);
    return response.data;
  }

  async getAvailableIPs(id: number): Promise<string[]> {
    const response = await this.api.get<string[]>(`/ranges/${id}/available-ips`);
    return response.data;
  }

  // ========== Devices ==========
  async getDevices(search?: string): Promise<Device[]> {
    const params = search ? { search } : {};
    const response = await this.api.get<Device[]>('/devices/', { params });
    return response.data;
  }

  async getDevice(id: number): Promise<Device> {
    const response = await this.api.get<Device>(`/devices/${id}`);
    return response.data;
  }

  async createDevice(data: DeviceCreate): Promise<Device> {
    const response = await this.api.post<Device>('/devices/', data);
    return response.data;
  }

  async updateDevice(id: number, data: DeviceUpdate): Promise<Device> {
    const response = await this.api.put<Device>(`/devices/${id}`, data);
    return response.data;
  }

  async deleteDevice(id: number): Promise<void> {
    await this.api.delete(`/devices/${id}`);
  }

  async suggestIP(rangeId: number): Promise<string> {
    const response = await this.api.get<{ suggested_ip: string }>(`/devices/suggest-ip/${rangeId}`);
    return response.data.suggested_ip;
  }

  // ========== DHCP Configuration ==========
  async generateDHCPConfig(): Promise<DHCPConfig> {
    const response = await this.api.post<DHCPConfig>('/dhcp/generate');
    return response.data;
  }

  async previewDHCPConfig(): Promise<string> {
    const response = await this.api.get<{ config_content: string }>('/dhcp/preview');
    return response.data.config_content;
  }

  async getActiveDHCPConfig(): Promise<DHCPConfig> {
    const response = await this.api.get<DHCPConfig>('/dhcp/active');
    return response.data;
  }

  async downloadDHCPConfig(): Promise<Blob> {
    const response = await this.api.get('/dhcp/download', {
      responseType: 'blob',
    });
    return response.data;
  }

  async getDHCPHistory(): Promise<DHCPConfig[]> {
    const response = await this.api.get<DHCPConfig[]>('/dhcp/history');
    return response.data;
  }

  async getDHCPStatus(): Promise<DHCPStatus> {
    const response = await this.api.get<DHCPStatus>('/dhcp/status');
    return response.data;
  }

  async activateDHCPConfig(): Promise<DHCPActivateResponse> {
    const response = await this.api.post<DHCPActivateResponse>('/dhcp/activate');
    return response.data;
  }

  // ========== Statistics ==========
  async getOverviewStats(): Promise<OverviewStatistics> {
    const response = await this.api.get<OverviewStatistics>('/stats/overview');
    return response.data;
  }

  async getDevicesByRange(): Promise<DevicesByRangeStats> {
    const response = await this.api.get<DevicesByRangeStats>('/stats/devices-by-range');
    return response.data;
  }

  async getRecentDevices(limit: number = 10): Promise<{ devices: RecentDevice[] }> {
    const response = await this.api.get<{ devices: RecentDevice[] }>('/stats/recent-devices', {
      params: { limit },
    });
    return response.data;
  }

  async getActivityTimeline(days: number = 7): Promise<ActivityTimelineResponse> {
    const response = await this.api.get<ActivityTimelineResponse>('/stats/device-activity-timeline', {
      params: { days },
    });
    return response.data;
  }

  async getDHCPEvents(hours: number = 24): Promise<DHCPEventsResponse> {
    const response = await this.api.get<DHCPEventsResponse>('/stats/dhcp-events', {
      params: { hours },
    });
    return response.data;
  }

  async getTopActiveDevices(limit: number = 10, days: number = 7): Promise<TopActiveDevicesResponse> {
    const response = await this.api.get<TopActiveDevicesResponse>('/stats/top-active-devices', {
      params: { limit, days },
    });
    return response.data;
  }

  // ========== User Management ==========
  async getUsers(): Promise<User[]> {
    const response = await this.api.get<User[]>('/users/');
    return response.data;
  }

  async getUser(id: number): Promise<User> {
    const response = await this.api.get<User>(`/users/${id}/`);
    return response.data;
  }

  async createUser(data: UserCreate): Promise<User> {
    const response = await this.api.post<User>('/users/', data);
    return response.data;
  }

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    const response = await this.api.put<User>(`/users/${id}/`, data);
    return response.data;
  }

  async deleteUser(id: number): Promise<void> {
    await this.api.delete(`/users/${id}/`);
  }

  // ========== Syslog ==========
  async getSyslogMessages(params?: {
    skip?: number;
    limit?: number;
    severity?: string;
    program?: string;
    hostname?: string;
    source_ip?: string;
    search?: string;
    hours?: number;
  }): Promise<SyslogMessage[]> {
    const response = await this.api.get<SyslogMessage[]>('/syslog/', { params });
    return response.data;
  }

  async getSyslogStats(hours: number = 24): Promise<SyslogStats> {
    const response = await this.api.get<SyslogStats>('/syslog/stats', {
      params: { hours }
    });
    return response.data;
  }

  async getSyslogCount(params?: {
    severity?: string;
    program?: string;
    hostname?: string;
    source_ip?: string;
    search?: string;
    hours?: number;
  }): Promise<{ total: number }> {
    const response = await this.api.get<{ total: number }>('/syslog/count', { params });
    return response.data;
  }

  async deleteSyslogMessage(id: number): Promise<void> {
    await this.api.delete(`/syslog/${id}/`);
  }

  async deleteOldLogs(days: number): Promise<{ deleted: number }> {
    const response = await this.api.delete<{ deleted: number }>('/syslog/bulk', {
      params: { days }
    });
    return response.data;
  }

  // ========== Settings ==========
  async getSettings(): Promise<Setting[]> {
    const response = await this.api.get<Setting[]>('/settings/');
    return response.data;
  }

  async getSetting(key: string): Promise<Setting> {
    const response = await this.api.get<Setting>(`/settings/${key}/`);
    return response.data;
  }

  async updateSetting(key: string, data: SettingUpdate): Promise<Setting> {
    const response = await this.api.put<Setting>(`/settings/${key}/`, data);
    return response.data;
  }

  // ========== DHCP Logs ==========
  async getDHCPLogs(params?: {
    lines?: number;
    search?: string;
    order?: 'asc' | 'desc';
  }): Promise<any> {
    const response = await this.api.get('/logs/dhcp', { params });
    return response.data;
  }

  async clearDHCPLogs(): Promise<any> {
    const response = await this.api.delete('/logs/clear');
    return response.data;
  }

  async listLogFiles(): Promise<any[]> {
    const response = await this.api.get('/logs/files');
    return response.data;
  }

  async deleteLogFile(filename: string): Promise<any> {
    const response = await this.api.delete(`/logs/file/${filename}`);
    return response.data;
  }
}

export const apiService = new ApiService();
