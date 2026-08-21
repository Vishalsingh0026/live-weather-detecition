import React, { useState } from 'react'
import type { Alert } from '../types'
import { formatDate, getTimeAgo } from '../utils/constants'

interface AlertsPanelProps {
  alerts: Alert[]
}

const SEVERITY_COLORS = {
  critical: 'bg-red-900 text-red-200 border-red-700',
  high: 'bg-orange-900 text-orange-200 border-orange-700',
  medium: 'bg-yellow-900 text-yellow-200 border-yellow-700',
  low: 'bg-green-900 text-green-200 border-green-700',
}

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  const [filter, setFilter] = useState<'all' | 'unsent' | 'sent'>('all')

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'unsent') return !alert.is_sent
    if (filter === 'sent') return alert.is_sent
    return true
  })

  const unsentCount = alerts.filter(a => !a.is_sent).length
  const sentCount = alerts.filter(a => a.is_sent).length

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <p className="text-slate-400 text-sm mb-2">Total Alerts</p>
          <p className="text-3xl font-bold">{alerts.length}</p>
        </div>
        <div className="bg-slate-800 border border-red-900 rounded-lg p-4">
          <p className="text-red-400 text-sm mb-2">Unsent</p>
          <p className="text-3xl font-bold text-red-400">{unsentCount}</p>
        </div>
        <div className="bg-slate-800 border border-green-900 rounded-lg p-4">
          <p className="text-green-400 text-sm mb-2">Sent</p>
          <p className="text-3xl font-bold text-green-400">{sentCount}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          All ({alerts.length})
        </button>
        <button
          onClick={() => setFilter('unsent')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'unsent'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Unsent ({unsentCount})
        </button>
        <button
          onClick={() => setFilter('sent')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'sent'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Sent ({sentCount})
        </button>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length > 0 ? (
          filteredAlerts.map(alert => (
            <div
              key={alert.id}
              className={`border rounded-lg p-4 ${
                SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold">{alert.title}</h4>
                  <p className="text-sm mt-1 opacity-90">{alert.message}</p>
                </div>
                <div className="flex items-center gap-2">
                  {alert.is_sent ? (
                    <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-semibold">
                      ✓ Sent
                    </span>
                  ) : (
                    <span className="bg-red-600 text-white px-2 py-1 rounded text-xs font-semibold">
                      ! Pending
                    </span>
                  )}
                </div>
              </div>

              <div className="flex justify-between items-center text-xs opacity-75 mt-2">
                <span>
                  {alert.is_sent
                    ? `Sent: ${formatDate(alert.sent_at || '')}`
                    : `Created: ${getTimeAgo(alert.created_at)}`}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 text-slate-400">
            <p>No alerts in this category</p>
          </div>
        )}
      </div>
    </div>
  )
}
