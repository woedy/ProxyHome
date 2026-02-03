import axios from 'axios'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types'

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // In development with Vite proxy, use relative URLs
  if (import.meta.env.DEV) {
    return '/api'
  }

  // In production or when VITE_API_URL is set
  return import.meta.env.VITE_API_URL || '/api'
}

const API_BASE_URL = getApiBaseUrl()

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await api.post('/auth/token/refresh/', { refresh: refreshToken })
          const { access } = response.data

          localStorage.setItem('auth_token', access)
          originalRequest.headers.Authorization = `Bearer ${access}`

          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear auth and redirect
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    if (error.response?.status === 401) {
      // Handle unauthorized access when refresh also fails
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// API endpoints
export const authApi = {
  login: (data: LoginRequest): Promise<{ data: AuthResponse }> =>
    api.post('/auth/login/', data),
  register: (data: RegisterRequest): Promise<{ data: AuthResponse }> =>
    api.post('/auth/register/', data),
  logout: (refreshToken: string) =>
    api.post('/auth/logout/', { refresh: refreshToken }),
  refreshToken: (refreshToken: string) =>
    api.post('/auth/token/refresh/', { refresh: refreshToken }),
  getProfile: (): Promise<{ data: User }> =>
    api.get('/auth/profile/'),
  updateProfile: (data: Partial<User>): Promise<{ data: User }> =>
    api.patch('/auth/profile/', data),
}

export const proxyApi = {
  // Proxies
  getProxies: (params?: any) => api.get('/proxies/', { params }),
  getProxy: (id: number) => api.get(`/proxies/${id}/`),
  createProxy: (data: any) => api.post('/proxies/', data),
  updateProxy: (id: number, data: any) => api.put(`/proxies/${id}/`, data),
  partialUpdateProxy: (id: number, data: any) => api.patch(`/proxies/${id}/`, data),
  deleteProxy: (id: number) => api.delete(`/proxies/${id}/`),
  bulkActions: (data: any) => api.post('/proxies/bulk_actions/', data),
  testProxies: (proxyIds: number[]) => api.post('/proxies/test_proxies/', { proxy_ids: proxyIds }),
  testSingleProxy: (id: number) => api.post(`/proxies/${id}/test_single/`),
  exportProxies: (format: string, filters?: any, proxy_ids?: number[]) =>
    api.post('/proxies/export/', { format, proxy_ids }, { params: filters }),
  cleanupProxies: (days: number) => api.delete('/proxies/cleanup/', { params: { days } }),
  deleteAllProxies: () => api.delete('/proxies/delete_all/', { params: { confirm: 'yes' } }),
  getStats: () => api.get('/proxies/stats/'),
  getFiltersInfo: () => api.get('/proxies/filters_info/'),

  // Credentials
  getCredentials: (params?: any) => api.get('/credentials/', { params }),
  getCredential: (id: number) => api.get(`/credentials/${id}/`),
  createCredentials: (data: any) => api.post('/credentials/', data),
  updateCredentials: (id: number, data: any) => api.put(`/credentials/${id}/`, data),
  partialUpdateCredentials: (id: number, data: any) => api.patch(`/credentials/${id}/`, data),
  deleteCredentials: (id: number) => api.delete(`/credentials/${id}/`),
  testCredentials: (serviceName: string, credentials: any) =>
    api.post('/credentials/test_credentials/', { service_name: serviceName, credentials }),
  testSingleCredentials: (id: number) => api.post(`/credentials/${id}/test_single/`),

  // Sources
  getSources: (params?: any) => api.get('/sources/', { params }),
  getSource: (id: number) => api.get(`/sources/${id}/`),
  getSourcePerformanceStats: () => api.get('/sources/performance_stats/'),

  // Jobs
  getJobs: (params?: any) => api.get('/jobs/', { params }),
  getJob: (id: number) => api.get(`/jobs/${id}/`),
  startFetch: (jobType: string, options?: any) =>
    api.post('/jobs/start_fetch/', { job_type: jobType, ...options }),
  clearAllJobs: () => api.delete('/jobs/clear_all/', { params: { confirm: 'yes' } }),
  getJobStats: () => api.get('/jobs/job_stats/'),

  // Tests
  getTests: (params?: any) => api.get('/tests/', { params }),
  getTest: (id: number) => api.get(`/tests/${id}/`),
  clearAllTests: () => api.delete('/tests/clear_all/', { params: { confirm: 'yes' } }),
  getTestStats: () => api.get('/tests/test_stats/'),
}

export default api