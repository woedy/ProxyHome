import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { proxyApi } from '../services/api'
import { ProxyCredentials } from '../types'
import toast from 'react-hot-toast'

export const useCredentials = () => {
  return useQuery({
    queryKey: ['credentials'],
    queryFn: () => proxyApi.getCredentials(),
    select: (response) => response.data.results as ProxyCredentials[],
  })
}

export const useCreateCredentials = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: Partial<ProxyCredentials>) => proxyApi.createCredentials(data),
    onSuccess: () => {
      toast.success('Credentials created successfully')
      queryClient.invalidateQueries({ queryKey: ['credentials'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create credentials')
    },
  })
}

export const useUpdateCredentials = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProxyCredentials> }) => 
      proxyApi.updateCredentials(id, data),
    onSuccess: () => {
      toast.success('Credentials updated successfully')
      queryClient.invalidateQueries({ queryKey: ['credentials'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update credentials')
    },
  })
}

export const useDeleteCredentials = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => proxyApi.deleteCredentials(id),
    onSuccess: () => {
      toast.success('Credentials deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['credentials'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete credentials')
    },
  })
}

export const useTestCredentials = () => {
  return useMutation({
    mutationFn: ({ serviceName, credentials }: { serviceName: string; credentials: any }) => 
      proxyApi.testCredentials(serviceName, credentials),
    onSuccess: () => {
      toast.success('Credentials test started')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to test credentials')
    },
  })
}