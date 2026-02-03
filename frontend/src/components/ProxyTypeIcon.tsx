import React from 'react'
import { GlobeAltIcon, ShieldCheckIcon, LockClosedIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

interface ProxyTypeIconProps {
  type: 'http' | 'socks4' | 'socks5'
  className?: string
}

export default function ProxyTypeIcon({ type, className }: ProxyTypeIconProps) {
  const getIcon = () => {
    switch (type) {
      case 'http':
        return <GlobeAltIcon className={clsx('h-4 w-4', className)} />
      case 'socks4':
        return <ShieldCheckIcon className={clsx('h-4 w-4', className)} />
      case 'socks5':
        return <LockClosedIcon className={clsx('h-4 w-4', className)} />
      default:
        return <GlobeAltIcon className={clsx('h-4 w-4', className)} />
    }
  }

  const getColor = () => {
    switch (type) {
      case 'http':
        return 'text-blue-500'
      case 'socks4':
        return 'text-green-500'
      case 'socks5':
        return 'text-purple-500'
      default:
        return 'text-gray-500'
    }
  }

  return (
    <div className={clsx('inline-flex items-center', getColor())}>
      {getIcon()}
      <span className="ml-1 text-xs font-medium uppercase">{type}</span>
    </div>
  )
}