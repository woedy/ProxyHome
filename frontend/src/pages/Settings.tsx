import React, { useState } from 'react'
import { useCleanupProxies, useDeleteAllProxies, useClearAllTests } from '../hooks/useProxies'
import { useClearAllJobs } from '../hooks/useJobs'
import { 
  TrashIcon,
  CogIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function Settings() {
  const [cleanupDays, setCleanupDays] = useState(7)
  const cleanupProxies = useCleanupProxies()
  const deleteAllProxies = useDeleteAllProxies()
  const clearAllJobs = useClearAllJobs()
  const clearAllTests = useClearAllTests()

  const handleCleanup = () => {
    if (confirm(`Are you sure you want to delete non-working proxies older than ${cleanupDays} days?`)) {
      cleanupProxies.mutate(cleanupDays)
    }
  }

  const handleDeleteAll = () => {
    if (confirm('⚠️ WARNING: This will permanently delete ALL proxies in the database. This action cannot be undone. Are you absolutely sure?')) {
      if (confirm('This is your final confirmation. Click OK to delete ALL proxies permanently.')) {
        deleteAllProxies.mutate()
      }
    }
  }

  const handleClearAllJobs = () => {
    if (confirm('⚠️ WARNING: This will permanently delete ALL job history and data. This action cannot be undone. Are you absolutely sure?')) {
      if (confirm('This is your final confirmation. Click OK to clear ALL job data permanently.')) {
        clearAllJobs.mutate()
      }
    }
  }

  const handleClearAllTests = () => {
    if (confirm('⚠️ WARNING: This will permanently delete ALL test history and data. This action cannot be undone. Are you absolutely sure?')) {
      if (confirm('This is your final confirmation. Click OK to clear ALL test data permanently.')) {
        clearAllTests.mutate()
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure your proxy platform settings</p>
      </div>

      {/* Cleanup Settings */}
      <div className="card p-6">
        <div className="flex items-center mb-4">
          <TrashIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">Proxy Cleanup</h2>
        </div>
        
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 mr-2 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800">
                  Automatic Cleanup
                </h3>
                <p className="text-sm text-yellow-700 mt-1">
                  This will permanently delete non-working proxies older than the specified number of days.
                  This action cannot be undone.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delete proxies older than
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={cleanupDays}
                  onChange={(e) => setCleanupDays(parseInt(e.target.value))}
                  className="input w-20"
                />
                <span className="text-sm text-gray-600">days</span>
              </div>
            </div>
            <div className="pt-6">
              <button
                onClick={handleCleanup}
                disabled={cleanupProxies.isPending}
                className="btn btn-danger"
              >
                <TrashIcon className="h-4 w-4 mr-2" />
                Clean Up Now
              </button>
            </div>
          </div>

          {/* Delete All Section */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-red-800">
                    Danger Zone
                  </h3>
                  <p className="text-sm text-red-700 mt-1">
                    These actions will permanently delete data from the database. These actions cannot be undone.
                  </p>
                  <div className="mt-3 space-y-2">
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={handleDeleteAll}
                        disabled={deleteAllProxies.isPending}
                        className="btn bg-red-600 hover:bg-red-700 text-white border-red-600 hover:border-red-700"
                      >
                        <TrashIcon className="h-4 w-4 mr-2" />
                        {deleteAllProxies.isPending ? 'Deleting...' : 'Delete All Proxies'}
                      </button>
                      <button
                        onClick={handleClearAllJobs}
                        disabled={clearAllJobs.isPending}
                        className="btn bg-red-600 hover:bg-red-700 text-white border-red-600 hover:border-red-700"
                      >
                        <TrashIcon className="h-4 w-4 mr-2" />
                        {clearAllJobs.isPending ? 'Clearing...' : 'Clear All Jobs'}
                      </button>
                      <button
                        onClick={handleClearAllTests}
                        disabled={clearAllTests.isPending}
                        className="btn bg-red-600 hover:bg-red-700 text-white border-red-600 hover:border-red-700"
                      >
                        <TrashIcon className="h-4 w-4 mr-2" />
                        {clearAllTests.isPending ? 'Clearing...' : 'Clear All Tests'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card p-6">
        <div className="flex items-center mb-4">
          <InformationCircleIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">System Information</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">Platform Features</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Multi-tier proxy fetching (Premium, Public, Basic)</li>
              <li>• Real-time proxy validation</li>
              <li>• Location detection for all proxies</li>
              <li>• Support for HTTP, SOCKS4, and SOCKS5</li>
              <li>• Background job processing with Celery</li>
              <li>• RESTful API with filtering and pagination</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">Supported Services</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Webshare (Premium)</li>
              <li>• Oxylabs (Premium)</li>
              <li>• Bright Data (Premium)</li>
              <li>• SmartProxy (Premium)</li>
              <li>• Free public proxy sources</li>
              <li>• GitHub proxy repositories</li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Information */}
      <div className="card p-6">
        <div className="flex items-center mb-4">
          <CogIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">API Endpoints</h2>
        </div>
        
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-md p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Available Endpoints</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="font-mono text-blue-600">GET /api/proxies/</div>
                <div className="text-gray-600">List all proxies with filtering</div>
              </div>
              <div>
                <div className="font-mono text-blue-600">GET /api/proxies/stats/</div>
                <div className="text-gray-600">Get proxy statistics</div>
              </div>
              <div>
                <div className="font-mono text-blue-600">POST /api/jobs/start_fetch/</div>
                <div className="text-gray-600">Start a new fetch job</div>
              </div>
              <div>
                <div className="font-mono text-blue-600">GET /api/jobs/</div>
                <div className="text-gray-600">List fetch jobs</div>
              </div>
              <div>
                <div className="font-mono text-blue-600">GET /api/credentials/</div>
                <div className="text-gray-600">Manage credentials</div>
              </div>
              <div>
                <div className="font-mono text-blue-600">GET /api/proxies/export/</div>
                <div className="text-gray-600">Export proxies (JSON/TXT/CSV)</div>
              </div>
            </div>
          </div>
          
          <div className="text-sm text-gray-600">
            <p>
              All endpoints support standard HTTP methods and return JSON responses.
              Use query parameters for filtering, pagination, and search functionality.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}