import { useState, useEffect } from 'react'
import { useProxies, useTestProxies, useExportProxies, useCleanupProxies, useDeleteAllProxies, useBulkActions, useFiltersInfo } from '../hooks/useProxies'
import { ProxyFilters } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import ProxyTypeIcon from '../components/ProxyTypeIcon'
import Pagination from '../components/Pagination'
import AdvancedFilters from '../components/AdvancedFilters'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  PlayIcon,
  CheckIcon,
  XMarkIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'
import clsx from 'clsx'

export default function ProxyList() {
  const [filters, setFilters] = useState<ProxyFilters>({
    page: 1,
    page_size: 25,
  })
  const [selectedProxies, setSelectedProxies] = useState<number[]>([])
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [showBulkMenu, setShowBulkMenu] = useState(false)

  const { data, isLoading, error } = useProxies(filters)
  const { data: filterInfo } = useFiltersInfo()
  const testProxies = useTestProxies()
  const exportProxies = useExportProxies()
  const cleanupProxies = useCleanupProxies()
  const deleteAllProxies = useDeleteAllProxies()
  const bulkActions = useBulkActions()

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowExportMenu(false)
      setShowBulkMenu(false)
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  const handleFiltersChange = (newFilters: ProxyFilters) => {
    setFilters(newFilters)
    setSelectedProxies([]) // Clear selection when filters change
  }

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }))
  }

  const handlePageSizeChange = (pageSize: number) => {
    setFilters(prev => ({ ...prev, page_size: pageSize, page: 1 }))
  }

  const handleSearchChange = (search: string) => {
    setFilters(prev => ({ ...prev, search: search || undefined, page: 1 }))
  }

  const handleOrderingChange = (ordering: string) => {
    setFilters(prev => ({ ...prev, ordering, page: 1 }))
  }

  const handleSelectProxy = (id: number) => {
    setSelectedProxies(prev =>
      prev.includes(id)
        ? prev.filter(p => p !== id)
        : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    if (selectedProxies.length === data?.results.length) {
      setSelectedProxies([])
    } else {
      setSelectedProxies(data?.results.map(p => p.id) || [])
    }
  }

  const handleBulkAction = (action: string) => {
    if (selectedProxies.length === 0) return

    const confirmMessages = {
      delete: 'Are you sure you want to delete the selected proxies?',
      test: 'Start testing the selected proxies?',
      mark_working: 'Mark selected proxies as working?',
      mark_failed: 'Mark selected proxies as failed?'
    }

    const message = confirmMessages[action as keyof typeof confirmMessages]
    if (message && !confirm(message)) return

    bulkActions.mutate({
      proxy_ids: selectedProxies,
      action: action as any
    }, {
      onSuccess: () => {
        setSelectedProxies([])
        setShowBulkMenu(false)
      }
    })
  }

  const handleExport = (format: string) => {
    exportProxies.mutate({
      format,
      filters,
      proxy_ids: selectedProxies.length > 0 ? selectedProxies : undefined
    })
    setShowExportMenu(false)
  }

  const handleCleanup = () => {
    if (confirm('Are you sure you want to delete old non-working proxies?')) {
      cleanupProxies.mutate(7) // Delete proxies older than 7 days
    }
  }

  const handleDeleteAll = () => {
    if (confirm('⚠️ WARNING: This will permanently delete ALL proxies in the database. This action cannot be undone. Are you absolutely sure?')) {
      if (confirm('This is your final confirmation. Click OK to delete ALL proxies permanently.')) {
        deleteAllProxies.mutate()
      }
    }
  }

  const getTierBadge = (tier: number) => {
    const tierNames = { 1: 'Premium', 2: 'Public', 3: 'Basic' }
    const tierColors = { 1: 'badge-info', 2: 'badge-success', 3: 'badge-warning' }
    return (
      <span className={clsx('badge', tierColors[tier as keyof typeof tierColors])}>
        {tierNames[tier as keyof typeof tierNames]}
      </span>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600">Error loading proxies</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Proxies</h1>
          <p className="text-gray-600">
            {data?.count || 0} total proxies
            {selectedProxies.length > 0 && (
              <span className="ml-2 text-blue-600">
                ({selectedProxies.length} selected)
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={clsx(
              'btn',
              showAdvancedFilters ? 'btn-primary' : 'btn-secondary'
            )}
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            Advanced Filters
          </button>

          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation()
                setShowExportMenu(!showExportMenu)
              }}
              disabled={exportProxies.isPending}
              className="btn btn-secondary"
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              {exportProxies.isPending ? 'Exporting...' : 'Export'}
            </button>
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                <div className="py-1">
                  <button
                    onClick={() => handleExport('json')}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                  >
                    Export as JSON
                  </button>
                  <button
                    onClick={() => handleExport('txt')}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                  >
                    Export as TXT
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                  >
                    Export as CSV
                  </button>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleCleanup}
            className="btn btn-danger"
            disabled={cleanupProxies.isPending}
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            Cleanup
          </button>

          <button
            onClick={handleDeleteAll}
            className="btn bg-red-600 hover:bg-red-700 text-white border-red-600 hover:border-red-700"
            disabled={deleteAllProxies.isPending}
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            {deleteAllProxies.isPending ? 'Deleting...' : 'Delete All'}
          </button>
        </div>
      </div>

      {/* Quick Search and Sort */}
      <div className="card p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                className="input pl-10"
                placeholder="Search IP, country, city..."
                value={filters.search || ''}
                onChange={(e) => handleSearchChange(e.target.value)}
              />
            </div>
          </div>
          <div className="w-48">
            <select
              className="select"
              value={filters.ordering || ''}
              onChange={(e) => handleOrderingChange(e.target.value)}
            >
              <option value="">Default Order</option>
              <option value="-created_at">Newest First</option>
              <option value="created_at">Oldest First</option>
              <option value="-response_time">Slowest First</option>
              <option value="response_time">Fastest First</option>
              <option value="-success_count">Most Successful</option>
              <option value="success_count">Least Successful</option>
            </select>
          </div>
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <AdvancedFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterInfo={filterInfo}
          isOpen={showAdvancedFilters}
          onToggle={() => setShowAdvancedFilters(!showAdvancedFilters)}
        />
      )}

      {/* Selected Actions */}
      {selectedProxies.length > 0 && (
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {selectedProxies.length} proxies selected
            </span>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowBulkMenu(!showBulkMenu)
                  }}
                  className="btn btn-primary"
                  disabled={bulkActions.isPending}
                >
                  <EllipsisVerticalIcon className="h-4 w-4 mr-2" />
                  Bulk Actions
                </button>
                {showBulkMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                    <div className="py-1">
                      <button
                        onClick={() => handleBulkAction('test')}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                      >
                        <PlayIcon className="h-4 w-4 inline mr-2" />
                        Test Selected
                      </button>
                      <button
                        onClick={() => handleBulkAction('mark_working')}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                      >
                        <CheckIcon className="h-4 w-4 inline mr-2" />
                        Mark as Working
                      </button>
                      <button
                        onClick={() => handleBulkAction('mark_failed')}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                      >
                        <XMarkIcon className="h-4 w-4 inline mr-2" />
                        Mark as Failed
                      </button>
                      <hr className="my-1" />
                      <button
                        onClick={() => handleBulkAction('delete')}
                        className="block px-4 py-2 text-sm text-red-700 hover:bg-red-50 w-full text-left"
                      >
                        <TrashIcon className="h-4 w-4 inline mr-2" />
                        Delete Selected
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <button
                onClick={() => setSelectedProxies([])}
                className="btn btn-secondary"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Proxy Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>
                      <input
                        type="checkbox"
                        checked={selectedProxies.length === data?.results.length && data?.results.length > 0}
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                    </th>
                    <th>Proxy</th>
                    <th>Type</th>
                    <th>Tier</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Success Rate</th>
                    <th>Response Time</th>
                    <th>Source</th>
                    <th>Last Checked</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results.map((proxy) => (
                    <tr key={proxy.id} className="hover:bg-gray-50">
                      <td>
                        <input
                          type="checkbox"
                          checked={selectedProxies.includes(proxy.id)}
                          onChange={() => handleSelectProxy(proxy.id)}
                          className="rounded"
                        />
                      </td>
                      <td>
                        <div className="font-mono text-sm">
                          {proxy.ip}:{proxy.port}
                        </div>
                      </td>
                      <td>
                        <ProxyTypeIcon type={proxy.proxy_type} />
                      </td>
                      <td>
                        {getTierBadge(proxy.tier)}
                      </td>
                      <td>
                        <div className="text-sm">
                          {proxy.location_display || 'Unknown'}
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={proxy.is_working} />
                      </td>
                      <td>
                        <div className="text-sm">
                          {proxy.success_rate ? `${proxy.success_rate.toFixed(1)}%` : '-'}
                        </div>
                      </td>
                      <td>
                        <div className="text-sm">
                          {proxy.response_time ? `${proxy.response_time.toFixed(2)}s` : '-'}
                        </div>
                      </td>
                      <td>
                        <div className="text-sm text-gray-600">
                          {proxy.source_name}
                        </div>
                      </td>
                      <td>
                        <div className="text-sm text-gray-600">
                          {proxy.last_checked
                            ? format(new Date(proxy.last_checked), 'MMM dd, HH:mm')
                            : 'Never'
                          }
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data && (
              <Pagination
                currentPage={data.current_page}
                totalPages={data.total_pages}
                pageSize={data.page_size}
                totalCount={data.count}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                showPageSizeSelector={true}
                pageSizeOptions={[10, 25, 50, 100]}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}