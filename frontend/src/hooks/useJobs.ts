import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { proxyApi } from '../services/api'
import { FetchJob, FetchJobOptions, PaginatedResponse } from '../types'
import toast from 'react-hot-toast'

export const useJobs = (params?: any) => {
  return useQuery({
    queryKey: ['jobs', params],
    queryFn: () => proxyApi.getJobs(params),
    select: (response) => response.data as PaginatedResponse<FetchJob>,
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
  })
}

export const useJob = (id: number) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: () => proxyApi.getJob(id),
    select: (response) => response.data as FetchJob,
    enabled: !!id,
    refetchInterval: (data) => {
      // Stop refetching if job is completed or failed
      return data?.status === 'running' || data?.status === 'pending' ? 2000 : false
    },
  })
}

export const useStartFetch = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ jobType, options }: { jobType: string; options?: FetchJobOptions }) => 
      proxyApi.startFetch(jobType, options),
    onSuccess: (response) => {
      toast.success(response.data.message)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['proxy-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to start fetch job')
    },
  })
}

export const useClearAllJobs = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: () => proxyApi.clearAllJobs(),
    onSuccess: (response) => {
      toast.success(response.data.message || 'All jobs cleared successfully')
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['job-stats'] })
    },
    onError: (error: any) => {
      console.error('Clear jobs error:', error)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          error.message || 
                          'Failed to clear jobs'
      toast.error(errorMessage)
    },
  })
}