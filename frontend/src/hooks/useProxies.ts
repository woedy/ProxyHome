import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { proxyApi } from '../services/api'
import { ProxyFilters, PaginatedResponse, Proxy, BulkAction, FilterInfo } from '../types'
import toast from 'react-hot-toast'

export const useProxies = (filters?: ProxyFilters) => {
  return useQuery({
    queryKey: ['proxies', filters],
    queryFn: () => proxyApi.getProxies(filters),
    select: (response) => response.data as PaginatedResponse<Proxy>,
  })
}

export const useProxy = (id: number) => {
  return useQuery({
    queryKey: ['proxy', id],
    queryFn: () => proxyApi.getProxy(id),
    select: (response) => response.data as Proxy,
    enabled: !!id,
  })
}

export const useProxyStats = () => {
  return useQuery({
    queryKey: ['proxy-stats'],
    queryFn: () => proxyApi.getStats(),
    select: (response) => response.data,
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export const useFiltersInfo = () => {
  return useQuery({
    queryKey: ['filters-info'],
    queryFn: () => proxyApi.getFiltersInfo(),
    select: (response) => response.data as FilterInfo,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useCreateProxy = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) => proxyApi.createProxy(data),
    onSuccess: () => {
      toast.success('Proxy created successfully')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create proxy')
    },
  })
}

export const useUpdateProxy = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => proxyApi.updateProxy(id, data),
    onSuccess: () => {
      toast.success('Proxy updated successfully')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update proxy')
    },
  })
}

export const useDeleteProxy = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => proxyApi.deleteProxy(id),
    onSuccess: () => {
      toast.success('Proxy deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete proxy')
    },
  })
}

export const useBulkActions = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: BulkAction) => proxyApi.bulkActions(data),
    onSuccess: (response) => {
      toast.success(response.data.message)
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Bulk action failed')
    },
  })
}

export const useTestProxies = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (proxyIds: number[]) => proxyApi.testProxies(proxyIds),
    onSuccess: () => {
      toast.success('Proxy testing started')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to start proxy testing')
    },
  })
}

export const useExportProxies = () => {
  return useMutation({
    mutationFn: ({ format, filters, proxy_ids }: { format: string; filters?: ProxyFilters; proxy_ids?: number[] }) =>
      proxyApi.exportProxies(format, filters, proxy_ids),
    onSuccess: (response, variables) => {
      const format = variables.format
      let content: string
      let mimeType: string

      if (format === 'json') {
        // For JSON, response.data is already an object, so stringify it
        content = JSON.stringify(response.data, null, 2)
        mimeType = 'application/json'
      } else {
        // For TXT and CSV, response.data is already a string
        content = response.data
        mimeType = format === 'csv' ? 'text/csv' : 'text/plain'
      }

      // Create and download file
      const blob = new Blob([content], { type: mimeType })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `proxies.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success(`Proxies exported as ${format.toUpperCase()} successfully`)
    },
    onError: (error: any) => {
      console.error('Export error:', error)
      toast.error(error.response?.data?.error || error.response?.data?.detail || 'Failed to export proxies')
    },
  })
}

export const useCleanupProxies = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (days: number) => proxyApi.cleanupProxies(days),
    onSuccess: (response) => {
      toast.success(response.data.message || 'Proxies cleaned up successfully')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      console.error('Cleanup error:', error)
      const errorMessage = error.response?.data?.error ||
        error.response?.data?.detail ||
        error.message ||
        'Failed to cleanup proxies'
      toast.error(errorMessage)
    },
  })
}

export const useDeleteAllProxies = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => proxyApi.deleteAllProxies(),
    onSuccess: (response) => {
      toast.success(response.data.message || 'All proxies deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['proxies'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      console.error('Delete all error:', error)
      const errorMessage = error.response?.data?.error ||
        error.response?.data?.detail ||
        error.message ||
        'Failed to delete all proxies'
      toast.error(errorMessage)
    },
  })
}

export const useClearAllTests = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => proxyApi.clearAllTests(),
    onSuccess: (response) => {
      toast.success(response.data.message || 'All test data cleared successfully')
      queryClient.invalidateQueries({ queryKey: ['tests'] })
      queryClient.invalidateQueries({ queryKey: ['test-stats'] })
    },
    onError: (error: any) => {
      console.error('Clear tests error:', error)
      const errorMessage = error.response?.data?.error ||
        error.response?.data?.detail ||
        error.message ||
        'Failed to clear test data'
      toast.error(errorMessage)
    },
  })
}