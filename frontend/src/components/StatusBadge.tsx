import React from 'react'
import clsx from 'clsx'

interface StatusBadgeProps {
  status: boolean | string
  trueLabel?: string
  falseLabel?: string
  className?: string
}

export default function StatusBadge({ 
  status, 
  trueLabel = 'Working', 
  falseLabel = 'Failed',
  className 
}: StatusBadgeProps) {
  if (typeof status === 'boolean') {
    return (
      <span className={clsx(
        'badge',
        status ? 'badge-success' : 'badge-danger',
        className
      )}>
        <span className={clsx('status-dot', status ? 'status-working' : 'status-failed')} />
        {status ? trueLabel : falseLabel}
      </span>
    )
  }

  // Handle string status
  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
      case 'working':
        return 'badge-success'
      case 'failed':
      case 'error':
        return 'badge-danger'
      case 'running':
      case 'pending':
        return 'badge-warning'
      default:
        return 'badge-gray'
    }
  }

  return (
    <span className={clsx('badge', getStatusStyle(status), className)}>
      {status}
    </span>
  )
}