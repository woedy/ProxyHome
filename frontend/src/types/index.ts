export interface Proxy {
  id: number
  ip: string
  port: number
  proxy_type: 'http' | 'socks4' | 'socks5'
  tier: 1 | 2 | 3
  source_name: string
  username?: string
  password?: string
  country: string
  country_code: string
  region: string
  city: string
  timezone: string
  location_display: string
  is_working: boolean
  last_checked?: string
  response_time?: number
  success_count: number
  failure_count: number
  success_rate: number
  created_at: string
  updated_at: string
}

export interface ProxyCredentials {
  id: number
  service_name: string
  credentials: Record<string, any>
  is_active: boolean
  has_credentials: boolean
  credential_keys: string[]
  created_at: string
  updated_at: string
}

export interface ProxySource {
  id: number
  name: string
  tier: 1 | 2 | 3
  is_active: boolean
  last_fetch_at?: string
  last_success_at?: string
  total_fetched: number
  success_rate: number
}

export interface FetchJob {
  id: number
  job_type: 'premium' | 'public' | 'basic' | 'unified'
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  proxies_found: number
  proxies_working: number
  sources_tried: number
  sources_successful: number
  validate_proxies: boolean
  timeout: number
  max_workers: number
  log_messages: Array<{ timestamp: string; message: string }>
  error_message: string
  created_at: string
  duration?: number
}

export interface ProxyTest {
  id: number
  proxy: number
  proxy_display: string
  test_url: string
  success: boolean
  response_time?: number
  response_ip?: string
  error_message: string
  tested_at: string
}

export interface Stats {
  total_proxies: number
  working_proxies: number
  premium_proxies: number
  public_proxies: number
  basic_proxies: number
  countries: number
  proxy_types: Record<string, number>
  top_countries: Array<{ country: string; count: number }>
  recent_jobs: FetchJob[]
  success_rate: number
}

export interface PaginatedResponse<T> {
  count: number
  total_pages: number
  current_page: number
  page_size: number
  next?: string
  previous?: string
  results: T[]
}

export interface ProxyFilters {
  proxy_type?: string
  tier?: number
  is_working?: boolean
  country?: string
  country_code?: string
  city?: string
  region?: string
  source?: string
  source_id?: number
  response_time_min?: number
  response_time_max?: number
  success_rate_min?: number
  success_rate_max?: number
  created_after?: string
  created_before?: string
  last_checked_after?: string
  last_checked_before?: string
  proxy_types?: string[]
  tiers?: number[]
  countries?: string[]
  port_min?: number
  port_max?: number
  has_auth?: boolean
  search?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface BulkAction {
  proxy_ids: number[]
  action: 'delete' | 'test' | 'mark_working' | 'mark_failed'
}

export interface FilterInfo {
  proxy_types: Array<{ value: string; label: string }>
  tiers: Array<{ value: number; label: string }>
  countries: string[]
  sources: Array<{ id: number; name: string }>
}

export interface FetchJobOptions {
  validate?: boolean
  timeout?: number
  max_workers?: number
}

// Authentication types
export interface User {
  id: number
  email: string
  username: string
  is_premium: boolean
  proxy_access_limit: number
  created_at: string
}

export interface AuthResponse {
  user: User
  access: string
  refresh: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  password_confirm: string
}