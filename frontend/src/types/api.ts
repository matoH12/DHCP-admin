// API Types for DHCP Admin

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  role: 'RO' | 'RW' | 'ADMIN';
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  role: 'RO' | 'RW' | 'ADMIN';
}

export interface UserUpdate {
  email?: string;
  password?: string;
  is_active?: boolean;
  role?: 'RO' | 'RW' | 'ADMIN';
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface IPRange {
  id: number;
  name: string;
  network_address: string;
  cidr: number;
  gateway: string;
  dns_servers: string[];
  domain_name: string;
  description?: string;
  pool_start?: string;
  pool_end?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IPRangeCreate {
  name: string;
  network_address: string;
  cidr: number;
  gateway: string;
  dns_servers: string[];
  domain_name: string;
  description?: string;
  pool_start?: string;
  pool_end?: string;
}

export interface IPRangeStats {
  total_usable_ips: number;
  assigned_ips: number;
  available_ips: number;
  utilization_percent: number;
}

export interface Device {
  id: number;
  hostname: string;
  mac_address: string;
  ip_address: string;
  ip_range_id: number;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  last_seen?: string | null;
}

export interface DeviceCreate {
  hostname: string;
  mac_address: string;
  ip_address: string;
  ip_range_id: number;
  description?: string;
}

export interface DeviceUpdate {
  hostname?: string;
  mac_address?: string;
  ip_address?: string;
  ip_range_id?: number;
  description?: string;
  is_active?: boolean;
}

export interface DHCPConfig {
  id: number;
  version: number;
  config_content: string;
  file_path: string;
  generated_at: string;
  generated_by: number;
  is_active: boolean;
}

export interface OverviewStatistics {
  summary: {
    total_ranges: number;
    total_devices: number;
    active_devices: number;
    inactive_devices: number;
    total_usable_ips: number;
    total_assigned_ips: number;
    total_available_ips: number;
    overall_utilization_percent: number;
  };
  ranges: {
    id: number;
    name: string;
    network: string;
    assigned: number;
    available: number;
    utilization: number;
    total: number;
  }[];
  chart_data?: {
    utilization_by_range: ChartUtilizationData[];
  };
}

export interface DevicesByRangeStats {
  data: {
    range_name: string;
    network: string;
    device_count: number;
  }[];
}

export interface RecentDevice {
  id: number;
  hostname: string;
  mac_address: string;
  ip_address: string;
  range_name: string | null;
  created_at: string;
  is_active: boolean;
}

export interface SyslogMessage {
  id: number;
  timestamp: string;
  facility: string | null;
  severity: string | null;
  hostname: string | null;
  source_ip: string | null;
  program: string | null;
  message: string;
  raw_message: string | null;
  created_at: string;
}

export interface SyslogStats {
  total_messages: number;
  time_range_hours: number;
  severity_counts: Record<string, number>;
  top_programs: Array<{ program: string; count: number }>;
}

export interface Setting {
  key: string;
  value: string;
  description: string | null;
}

export interface SettingUpdate {
  value: string;
}

export interface DHCPStatus {
  pending_changes: boolean;
  active_config_version: number | null;
  active_config_generated_at: string | null;
}

export interface DHCPActivateResponse {
  success: boolean;
  message: string;
  version: number;
  file_path: string;
  generated_at: string;
  restart_status: string;
}

// ========== Analytics & Charts Types ==========

export interface ActivityTimelinePoint {
  date: string;
  active_devices: number;
  total_events: number;
}

export interface ActivityTimelineResponse {
  data: ActivityTimelinePoint[];
  days: number;
  period_start: string;
  period_end: string;
}

export interface DHCPEventData {
  name: string;
  value: number;
  color: string;
}

export interface DHCPEventsResponse {
  data: DHCPEventData[];
  total_events: number;
  time_range_hours: number;
}

export interface TopActiveDevice {
  device_id: number;
  hostname: string;
  ip_address: string;
  mac_address: string;
  activity_count: number;
  last_seen: string | null;
  range_name: string | null;
}

export interface TopActiveDevicesResponse {
  data: TopActiveDevice[];
  period_days: number;
}

export interface ChartUtilizationData {
  name: string;
  assigned: number;
  available: number;
  utilization: number;
  total: number;
}
