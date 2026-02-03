import { useState } from 'react'
import { useJobs, useStartFetch, useClearAllJobs } from '../hooks/useJobs'
import { FetchJobOptions } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import Pagination from '../components/Pagination'
import { 
  PlayIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'
import clsx from 'clsx'

export default function FetchJobs() {
  const [showStartModal, setShowStartModal] = useState(false)
  const [expandedJobs, setExpandedJobs] = useState<number[]>([])
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10
  })
  const [jobOptions, setJobOptions] = useState<FetchJobOptions & { job_type: string }>({
    job_type: 'unified',
    validate: true,
    timeout: 10,
    max_workers: 30
  })

  const { data, isLoading } = useJobs(filters)
  const startFetch = useStartFetch()
  const clearAllJobs = useClearAllJobs()

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }))
  }

  const handlePageSizeChange = (pageSize: number) => {
    setFilters(prev => ({ ...prev, page_size: pageSize, page: 1 }))
  }

  const handleStartJob = (e: React.FormEvent) => {
    e.preventDefault()
    const { job_type, ...options } = jobOptions
    startFetch.mutate({ jobType: job_type, options }, {
      onSuccess: () => setShowStartModal(false)
    })
  }

  const handleClearAllJobs = () => {
    if (confirm('⚠️ WARNING: This will permanently delete ALL job history and data. This action cannot be undone. Are you absolutely sure?')) {
      if (confirm('This is your final confirmation. Click OK to clear ALL job data permanently.')) {
        clearAllJobs.mutate()
      }
    }
  }

  const toggleJobExpansion = (jobId: number) => {
    setExpandedJobs(prev => 
      prev.includes(jobId)
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'running':
        return <LoadingSpinner size="sm" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
    }
  }

  const getJobTypeColor = (jobType: string) => {
    switch (jobType) {
      case 'premium':
        return 'bg-blue-100 text-blue-800'
      case 'public':
        return 'bg-green-100 text-green-800'
      case 'basic':
        return 'bg-yellow-100 text-yellow-800'
      case 'unified':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Fetch Jobs</h1>
          <p className="text-gray-600">Monitor proxy fetching operations</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleClearAllJobs}
            disabled={clearAllJobs.isPending}
            className="btn bg-red-600 hover:bg-red-700 text-white border-red-600 hover:border-red-700"
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            {clearAllJobs.isPending ? 'Clearing...' : 'Clear All Jobs'}
          </button>
          <button
            onClick={() => setShowStartModal(true)}
            className="btn btn-primary"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Start New Job
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { type: 'unified', label: 'Unified Fetch', description: 'All tiers combined' },
          { type: 'premium', label: 'Premium Only', description: 'High-quality proxies' },
          { type: 'public', label: 'Public Only', description: 'Free public sources' },
          { type: 'basic', label: 'Basic Only', description: 'Fallback sources' }
        ].map((job) => (
          <button
            key={job.type}
            onClick={() => startFetch.mutate({ jobType: job.type })}
            disabled={startFetch.isPending}
            className="card p-4 text-left hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <span className={clsx('badge', getJobTypeColor(job.type))}>
                {job.label}
              </span>
              <PlayIcon className="h-4 w-4 text-gray-400" />
            </div>
            <p className="text-sm text-gray-600">{job.description}</p>
          </button>
        ))}
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {data?.results.map((job) => (
          <div key={job.id} className="card">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(job.status)}
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-medium text-gray-900 capitalize">
                        {job.job_type} Fetch
                      </h3>
                      <StatusBadge status={job.status} />
                    </div>
                    <p className="text-sm text-gray-600">
                      Started {format(new Date(job.created_at), 'MMM dd, yyyy HH:mm')}
                      {job.duration && ` • Duration: ${job.duration.toFixed(1)}s`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {job.proxies_found} found
                    </div>
                    <div className="text-sm text-gray-600">
                      {job.proxies_working} working
                    </div>
                  </div>
                  <button
                    onClick={() => toggleJobExpansion(job.id)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {expandedJobs.includes(job.id) ? (
                      <ChevronDownIcon className="h-5 w-5" />
                    ) : (
                      <ChevronRightIcon className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedJobs.includes(job.id) && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Job Details */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Job Details</h4>
                      <dl className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Sources Tried:</dt>
                          <dd className="text-gray-900">{job.sources_tried}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Sources Successful:</dt>
                          <dd className="text-gray-900">{job.sources_successful}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Validation:</dt>
                          <dd className="text-gray-900">{job.validate_proxies ? 'Enabled' : 'Disabled'}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Timeout:</dt>
                          <dd className="text-gray-900">{job.timeout}s</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Max Workers:</dt>
                          <dd className="text-gray-900">{job.max_workers}</dd>
                        </div>
                      </dl>
                    </div>

                    {/* Error Message */}
                    {job.error_message && (
                      <div>
                        <h4 className="text-sm font-medium text-red-900 mb-2">Error</h4>
                        <div className="bg-red-50 border border-red-200 rounded-md p-3">
                          <p className="text-sm text-red-700">{job.error_message}</p>
                        </div>
                      </div>
                    )}

                    {/* Log Messages */}
                    {job.log_messages.length > 0 && (
                      <div className={job.error_message ? 'md:col-span-1' : 'md:col-span-2'}>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Log Messages</h4>
                        <div className="bg-gray-50 border border-gray-200 rounded-md p-3 max-h-40 overflow-y-auto">
                          <div className="space-y-1">
                            {job.log_messages.slice(-10).map((log, index) => (
                              <div key={index} className="text-xs">
                                <span className="text-gray-500">
                                  {format(new Date(log.timestamp), 'HH:mm:ss')}
                                </span>
                                <span className="ml-2 text-gray-700">{log.message}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {data?.results.length === 0 && (
          <div className="text-center py-12">
            <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs yet</h3>
            <p className="text-gray-600 mb-4">
              Start your first proxy fetch job to see results here
            </p>
            <button
              onClick={() => setShowStartModal(true)}
              className="btn btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Start Your First Job
            </button>
          </div>
        )}
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
          pageSizeOptions={[5, 10, 25, 50]}
        />
      )}

      {/* Start Job Modal */}
      {showStartModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Start New Fetch Job</h3>
              <button
                onClick={() => setShowStartModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleStartJob} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Type
                </label>
                <select
                  className="select"
                  value={jobOptions.job_type}
                  onChange={(e) => setJobOptions(prev => ({ ...prev, job_type: e.target.value }))}
                >
                  <option value="unified">Unified (All Tiers)</option>
                  <option value="premium">Premium Only</option>
                  <option value="public">Public Only</option>
                  <option value="basic">Basic Only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timeout (seconds)
                </label>
                <input
                  type="number"
                  className="input"
                  min="5"
                  max="60"
                  value={jobOptions.timeout}
                  onChange={(e) => setJobOptions(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Workers
                </label>
                <input
                  type="number"
                  className="input"
                  min="1"
                  max="100"
                  value={jobOptions.max_workers}
                  onChange={(e) => setJobOptions(prev => ({ ...prev, max_workers: parseInt(e.target.value) }))}
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="validate"
                  className="rounded"
                  checked={jobOptions.validate}
                  onChange={(e) => setJobOptions(prev => ({ ...prev, validate: e.target.checked }))}
                />
                <label htmlFor="validate" className="ml-2 text-sm text-gray-700">
                  Validate proxies (recommended)
                </label>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowStartModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={startFetch.isPending}
                  className="btn btn-primary"
                >
                  Start Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}