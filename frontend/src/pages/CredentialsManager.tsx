import React, { useState } from 'react'
import { useCredentials, useCreateCredentials, useUpdateCredentials, useDeleteCredentials, useTestCredentials } from '../hooks/useCredentials'
import { ProxyCredentials } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  KeyIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'
import clsx from 'clsx'

interface CredentialFormData {
  service_name: string
  credentials: Record<string, string>
  is_active: boolean
}

const SERVICE_TEMPLATES = {
  webshare: {
    name: 'Webshare',
    fields: [
      { key: 'api_key', label: 'API Key', type: 'password', placeholder: 'Your Webshare API key' }
    ]
  },
  oxylabs: {
    name: 'Oxylabs',
    fields: [
      { key: 'username', label: 'Username', type: 'text', placeholder: 'Your Oxylabs username' },
      { key: 'password', label: 'Password', type: 'password', placeholder: 'Your Oxylabs password' }
    ]
  },
  brightdata: {
    name: 'Bright Data',
    fields: [
      { key: 'username', label: 'Username', type: 'text', placeholder: 'Your Bright Data username' },
      { key: 'password', label: 'Password', type: 'password', placeholder: 'Your Bright Data password' },
      { key: 'endpoint', label: 'Endpoint', type: 'text', placeholder: 'Proxy endpoint URL' }
    ]
  },
  smartproxy: {
    name: 'SmartProxy',
    fields: [
      { key: 'username', label: 'Username', type: 'text', placeholder: 'Your SmartProxy username' },
      { key: 'password', label: 'Password', type: 'password', placeholder: 'Your SmartProxy password' }
    ]
  }
}

export default function CredentialsManager() {
  const [showModal, setShowModal] = useState(false)
  const [editingCredential, setEditingCredential] = useState<ProxyCredentials | null>(null)
  const [formData, setFormData] = useState<CredentialFormData>({
    service_name: '',
    credentials: {},
    is_active: true
  })

  const { data: credentials, isLoading } = useCredentials()
  const createCredentials = useCreateCredentials()
  const updateCredentials = useUpdateCredentials()
  const deleteCredentials = useDeleteCredentials()
  const testCredentials = useTestCredentials()

  const handleOpenModal = (credential?: ProxyCredentials) => {
    if (credential) {
      setEditingCredential(credential)
      setFormData({
        service_name: credential.service_name,
        credentials: {},
        is_active: credential.is_active
      })
    } else {
      setEditingCredential(null)
      setFormData({
        service_name: '',
        credentials: {},
        is_active: true
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingCredential(null)
    setFormData({
      service_name: '',
      credentials: {},
      is_active: true
    })
  }

  const handleServiceChange = (serviceName: string) => {
    setFormData(prev => ({
      ...prev,
      service_name: serviceName,
      credentials: {}
    }))
  }

  const handleCredentialFieldChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      credentials: {
        ...prev.credentials,
        [key]: value
      }
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (editingCredential) {
      updateCredentials.mutate({
        id: editingCredential.id,
        data: formData
      }, {
        onSuccess: () => handleCloseModal()
      })
    } else {
      createCredentials.mutate(formData, {
        onSuccess: () => handleCloseModal()
      })
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete these credentials?')) {
      deleteCredentials.mutate(id)
    }
  }

  const handleTest = (credential: ProxyCredentials) => {
    testCredentials.mutate({
      serviceName: credential.service_name,
      credentials: credential.credentials
    })
  }

  const getServiceTemplate = (serviceName: string) => {
    return SERVICE_TEMPLATES[serviceName as keyof typeof SERVICE_TEMPLATES]
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
          <h1 className="text-2xl font-bold text-gray-900">Credentials Manager</h1>
          <p className="text-gray-600">Manage premium proxy service credentials</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="btn btn-primary"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Credentials
        </button>
      </div>

      {/* Credentials List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {credentials?.map((credential) => (
          <div key={credential.id} className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <KeyIcon className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium text-gray-900 capitalize">
                  {credential.service_name}
                </h3>
              </div>
              <StatusBadge 
                status={credential.is_active} 
                trueLabel="Active" 
                falseLabel="Inactive" 
              />
            </div>

            <div className="space-y-2 mb-4">
              <div className="text-sm text-gray-600">
                <span className="font-medium">Credentials:</span>{' '}
                {credential.has_credentials ? 'Configured' : 'Not configured'}
              </div>
              {credential.credential_keys.length > 0 && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Fields:</span>{' '}
                  {credential.credential_keys.join(', ')}
                </div>
              )}
              <div className="text-sm text-gray-600">
                <span className="font-medium">Updated:</span>{' '}
                {format(new Date(credential.updated_at), 'MMM dd, yyyy')}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => handleTest(credential)}
                disabled={!credential.has_credentials || testCredentials.isPending}
                className="btn btn-secondary text-sm"
              >
                <PlayIcon className="h-3 w-3 mr-1" />
                Test
              </button>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleOpenModal(credential)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <PencilIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(credential.id)}
                  className="text-red-400 hover:text-red-600"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {credentials?.length === 0 && (
          <div className="col-span-full text-center py-12">
            <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No credentials configured</h3>
            <p className="text-gray-600 mb-4">
              Add premium proxy service credentials to access higher quality proxies
            </p>
            <button
              onClick={() => handleOpenModal()}
              className="btn btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Your First Credentials
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                {editingCredential ? 'Edit Credentials' : 'Add Credentials'}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service
                </label>
                <select
                  className="select"
                  value={formData.service_name}
                  onChange={(e) => handleServiceChange(e.target.value)}
                  required
                  disabled={!!editingCredential}
                >
                  <option value="">Select a service</option>
                  {Object.entries(SERVICE_TEMPLATES).map(([key, template]) => (
                    <option key={key} value={key}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>

              {formData.service_name && (
                <>
                  {getServiceTemplate(formData.service_name)?.fields.map((field) => (
                    <div key={field.key}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {field.label}
                      </label>
                      <input
                        type={field.type}
                        className="input"
                        placeholder={field.placeholder}
                        value={formData.credentials[field.key] || ''}
                        onChange={(e) => handleCredentialFieldChange(field.key, e.target.value)}
                        required
                      />
                    </div>
                  ))}

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_active"
                      className="rounded"
                      checked={formData.is_active}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    />
                    <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                      Active
                    </label>
                  </div>
                </>
              )}

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createCredentials.isPending || updateCredentials.isPending}
                  className="btn btn-primary"
                >
                  {editingCredential ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}