import React, { useMemo } from 'react'
import type { DashboardMetrics, Event } from '../types'
import { getSeverityColor, getSeverityLabel, EVENT_ICONS, EVENT_LABELS } from '../utils/constants'
import RiskScoreGauge from './RiskScoreGauge'
import EventsMap from './EventsMap'

interface DashboardProps {
  metrics: DashboardMetrics
  events: Event[]
}

export default function Dashboard({ metrics, events }: DashboardProps) {
  const criticalEvents = useMemo(() => events.filter(e => e.severity >= 85), [events])
  const highSeverityEvents = useMemo(() => events.filter(e => 70 <= e.severity < 85), [events])

  const eventsByType = useMemo(() => {
    const grouped: Record<string, number> = {}
    events.forEach(event => {
      grouped[event.event_type] = (grouped[event.event_type] || 0) + 1
    })
    return grouped
  }, [events])

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Active Events */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm mb-2">Active Events</p>
              <p className="text-4xl font-bold text-white">{metrics.total_active_events}</p>
            </div>
            <div className="text-5xl opacity-50">📊</div>
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="bg-slate-800 border border-red-900 rounded-lg p-6 hover:border-red-700 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-400 text-sm mb-2">Critical Alerts</p>
              <p className="text-4xl font-bold text-red-400">{metrics.critical_alerts}</p>
            </div>
            <div className="text-5xl opacity-50">🚨</div>
          </div>
        </div>

        {/* High Severity */}
        <div className="bg-slate-800 border border-orange-900 rounded-lg p-6 hover:border-orange-700 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-400 text-sm mb-2">High Severity</p>
              <p className="text-4xl font-bold text-orange-400">{metrics.high_severity_count}</p>
            </div>
            <div className="text-5xl opacity-50">⚠️</div>
          </div>
        </div>

        {/* Average Risk Score */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm mb-2">Avg Risk Score</p>
              <p className="text-4xl font-bold" style={{ color: getSeverityColor(metrics.average_risk_score) }}>
                {metrics.average_risk_score.toFixed(1)}
              </p>
            </div>
            <div className="text-5xl opacity-50">📈</div>
          </div>
        </div>
      </div>

      {/* Map and Risk Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
          <EventsMap events={events} />
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
          <RiskScoreGauge score={metrics.average_risk_score} />

          <div className="mt-6 space-y-2">
            <p className="text-sm text-slate-400">Last Updated:</p>
            <p className="text-sm text-slate-300">
              {new Date(metrics.last_updated).toLocaleTimeString()}
            </p>
          </div>
        </div>
      </div>

      {/* Events by Type */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Events by Type</h3>
          <div className="space-y-3">
            {Object.entries(eventsByType).length > 0 ? (
              Object.entries(eventsByType).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{EVENT_ICONS[type as keyof typeof EVENT_ICONS]}</span>
                    <span className="text-sm text-slate-300">
                      {EVENT_LABELS[type as keyof typeof EVENT_LABELS]}
                    </span>
                  </div>
                  <span className="bg-blue-900 text-blue-300 px-3 py-1 rounded-full text-sm font-semibold">
                    {count}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">No events detected</p>
            )}
          </div>
        </div>

        {/* Critical Events List */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 text-red-400">⚠️ Critical Events</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {criticalEvents.length > 0 ? (
              criticalEvents.map(event => (
                <div key={event.id} className="bg-slate-900 p-3 rounded border border-red-900">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-semibold text-red-400">{event.location}</span>
                    <span
                      className="px-2 py-1 rounded text-xs font-bold text-white"
                      style={{ backgroundColor: getSeverityColor(event.severity) }}
                    >
                      {event.severity}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{event.event_type.replace('_', ' ')}</p>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">No critical events</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
