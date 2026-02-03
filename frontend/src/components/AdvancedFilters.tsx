import { useState, useEffect } from 'react'
import { XMarkIcon, FunnelIcon } from '@heroicons/react/24/outline'
import { ProxyFilters, FilterInfo } from '../types'
import clsx from 'clsx'

interface AdvancedFiltersProps {
  filters: ProxyFilters
  onFiltersChange: (filters: ProxyFilters) => void
  filterInfo?: FilterInfo
  isOpen: boolean
  onToggle: () => void
  className?: string
}

export default function AdvancedFilters({
  filters,
  onFiltersChange,
  filterInfo,
  isOpen,
  onToggle,
  className
}: AdvancedFiltersProps) {
  const [localFilters, setLocalFilters] = useState<ProxyFilters>(filters)

  useEffect(() => {
    setLocalFilters(filters)
  }, [filters])

  const handleFilterChange = (key: keyof ProxyFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value }
    setLocalFilters(newFilters)
  }

  const applyFilters = () => {
    onFiltersChange({ ...localFilters, page: 1 })
  }

  const clearFilters = () => {
    const clearedFilters: ProxyFilters = {
      page: 1,
      page_size: filters.page_size
    }
    setLocalFilters(clearedFilters)
    onFiltersChange(clearedFilters)
  }

  const hasActiveFilters = () => {
    const { page, page_size, ...otherFilters } = localFilters
    return Object.values(otherFilters).some(value => 
      value !== undefined && value !== '' && 
      (Array.isArray(value) ? value.length > 0 : true)
    )
  }

  return (
    <div className={clsx('bg-white border border-gray-200 rounded-lg', className)}>
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900">Advanced Filters</h3>
          {hasActiveFilters() && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Active
            </span>
          )}
        </div>
        <button
          onClick={onToggle}
          className="text-gray-400 hover:text-gray-600"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      {isOpen && (
        <div className="p-4 space-y-6">
          {/* Basic Filters */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Basic Filters</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Proxy Type
                </label>
                <select
                  value={localFilters.proxy_type || ''}
                  onChange={(e) => handleFilterChange('proxy_type', e.target.value || undefined)}
                  className="input"
                >
                  <option value="">All Types</option>
                  {filterInfo?.proxy_types.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tier
                </label>
                <select
                  value={localFilters.tier || ''}
                  onChange={(e) => handleFilterChange('tier', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input"
                >
                  <option value="">All Tiers</option>
                  {filterInfo?.tiers.map((tier) => (
                    <option key={tier.value} value={tier.value}>
                      {tier.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={localFilters.is_working?.toString() || ''}
                  onChange={(e) => handleFilterChange('is_working', e.target.value === '' ? undefined : e.target.value === 'true')}
                  className="input"
                >
                  <option value="">All Status</option>
                  <option value="true">Working</option>
                  <option value="false">Failed</option>
                </select>
              </div>
            </div>
          </div>

          {/* Location Filters */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Location Filters</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country
                </label>
                <input
                  type="text"
                  value={localFilters.country || ''}
                  onChange={(e) => handleFilterChange('country', e.target.value || undefined)}
                  placeholder="e.g., United States"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country Code
                </label>
                <input
                  type="text"
                  value={localFilters.country_code || ''}
                  onChange={(e) => handleFilterChange('country_code', e.target.value || undefined)}
                  placeholder="e.g., US"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City
                </label>
                <input
                  type="text"
                  value={localFilters.city || ''}
                  onChange={(e) => handleFilterChange('city', e.target.value || undefined)}
                  placeholder="e.g., New York"
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Performance Filters */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Performance Filters</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Response Time (seconds)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value={localFilters.response_time_min || ''}
                    onChange={(e) => handleFilterChange('response_time_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="Min"
                    step="0.1"
                    className="input"
                  />
                  <input
                    type="number"
                    value={localFilters.response_time_max || ''}
                    onChange={(e) => handleFilterChange('response_time_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="Max"
                    step="0.1"
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Success Rate (%)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value={localFilters.success_rate_min || ''}
                    onChange={(e) => handleFilterChange('success_rate_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="Min"
                    min="0"
                    max="100"
                    className="input"
                  />
                  <input
                    type="number"
                    value={localFilters.success_rate_max || ''}
                    onChange={(e) => handleFilterChange('success_rate_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="Max"
                    min="0"
                    max="100"
                    className="input"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Port Range */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Port Range</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Port Range
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value={localFilters.port_min || ''}
                    onChange={(e) => handleFilterChange('port_min', e.target.value ? parseInt(e.target.value) : undefined)}
                    placeholder="Min Port"
                    min="1"
                    max="65535"
                    className="input"
                  />
                  <input
                    type="number"
                    value={localFilters.port_max || ''}
                    onChange={(e) => handleFilterChange('port_max', e.target.value ? parseInt(e.target.value) : undefined)}
                    placeholder="Max Port"
                    min="1"
                    max="65535"
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Authentication
                </label>
                <select
                  value={localFilters.has_auth?.toString() || ''}
                  onChange={(e) => handleFilterChange('has_auth', e.target.value === '' ? undefined : e.target.value === 'true')}
                  className="input"
                >
                  <option value="">All Proxies</option>
                  <option value="true">With Authentication</option>
                  <option value="false">Without Authentication</option>
                </select>
              </div>
            </div>
          </div>

          {/* Date Filters */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Date Filters</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Created Date
                </label>
                <div className="flex space-x-2">
                  <input
                    type="datetime-local"
                    value={localFilters.created_after || ''}
                    onChange={(e) => handleFilterChange('created_after', e.target.value || undefined)}
                    className="input"
                  />
                  <input
                    type="datetime-local"
                    value={localFilters.created_before || ''}
                    onChange={(e) => handleFilterChange('created_before', e.target.value || undefined)}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Checked
                </label>
                <div className="flex space-x-2">
                  <input
                    type="datetime-local"
                    value={localFilters.last_checked_after || ''}
                    onChange={(e) => handleFilterChange('last_checked_after', e.target.value || undefined)}
                    className="input"
                  />
                  <input
                    type="datetime-local"
                    value={localFilters.last_checked_before || ''}
                    onChange={(e) => handleFilterChange('last_checked_before', e.target.value || undefined)}
                    className="input"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              onClick={clearFilters}
              className="btn btn-secondary"
              disabled={!hasActiveFilters()}
            >
              Clear All Filters
            </button>
            <div className="flex space-x-3">
              <button
                onClick={onToggle}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={applyFilters}
                className="btn btn-primary"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}