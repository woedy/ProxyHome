import React from 'react'
import { useProxyStats } from '../hooks/useProxies'
import { useJobs } from '../hooks/useJobs'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { 
  ServerIcon, 
  CheckCircleIcon, 
  GlobeAltIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useProxyStats()
  const { data: jobsData, isLoading: jobsLoading } = useJobs({ page_size: 5 })

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const tierData = [
    { name: 'Premium', value: stats?.premium_proxies || 0, color: '#3B82F6' },
    { name: 'Public', value: stats?.public_proxies || 0, color: '#10B981' },
    { name: 'Basic', value: stats?.basic_proxies || 0, color: '#F59E0B' },
  ]

  const typeData = Object.entries(stats?.proxy_types || {}).map(([type, count]) => ({
    name: type.toUpperCase(),
    value: count,
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your proxy infrastructure</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ServerIcon className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Proxies</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.total_proxies || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-6 w-6 text-green-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Working Proxies</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.working_proxies || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <GlobeAltIcon className="h-6 w-6 text-blue-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Countries</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.countries || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-6 w-6 text-purple-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.success_rate || 0}%</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Proxy Types Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Proxy Types</h3>
          {typeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              No data available
            </div>
          )}
        </div>

        {/* Tier Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Tier Distribution</h3>
          {tierData.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={tierData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {tierData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              No data available
            </div>
          )}
        </div>
      </div>

      {/* Top Countries and Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Countries */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Countries</h3>
          <div className="space-y-3">
            {stats?.top_countries?.slice(0, 5).map((country, index) => (
              <div key={country.country} className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-900">{country.country}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-500">{country.count} proxies</span>
                </div>
              </div>
            )) || (
              <div className="text-gray-500 text-sm">No countries data available</div>
            )}
          </div>
        </div>

        {/* Recent Jobs */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Jobs</h3>
          <div className="space-y-3">
            {jobsLoading ? (
              <LoadingSpinner />
            ) : jobsData?.results?.length ? (
              jobsData.results.map((job) => (
                <div key={job.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {job.job_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {job.proxies_found} found
                    </span>
                    <StatusBadge status={job.status} />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-sm">No recent jobs</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}