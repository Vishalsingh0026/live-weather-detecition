import React, { useState } from 'react'
import type { Event } from '../types'
import { getSeverityColor, getSeverityLabel, EVENT_ICONS, EVENT_LABELS, getTimeAgo } from '../utils/constants'

interface EventsListProps {
  events: Event[]
}

export default function EventsList({ events }: EventsListProps) {
  const [sortBy, setSortBy] = useState<'severity' | 'time'>('severity')
  const [filterType, setFilterType] = useState<string>('all')

  const filteredEvents = events.filter(
    e => filterType === 'all' || e.event_type === filterType
  )

  const sortedEvents = [...filteredEvents].sort((a, b) => {
    if (sortBy === 'severity') {
      return b.severity - a.severity
    } else {
      return new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()
    }
  })

  const uniqueTypes = Array.from(new Set(events.map(e => e.event_type)))

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4 flex-wrap">
        <div>
          <label className="text-sm text-slate-400 block mb-2">Sort By:</label>
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value as 'severity' | 'time')}
            className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          >
            <option value="severity">Severity (High to Low)</option>
            <option value="time">Time (Newest First)</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-slate-400 block mb-2">Filter Type:</label>
          <select
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
            className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          >
            <option value="all">All Events</option>
            {uniqueTypes.map(type => (
              <option key={type} value={type}>
                {EVENT_LABELS[type as keyof typeof EVENT_LABELS]}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Events Table */}
      <div className="overflow-x-auto">
        {sortedEvents.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Type</th>
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Location</th>
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Severity</th>
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Confidence</th>
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Detected</th>
                <th className="text-left px-4 py-3 text-slate-400 font-semibold">Source</th>
              </tr>
            </thead>
            <tbody>
              {sortedEvents.map(event => (
                <tr
                  key={event.id}
                  className="border-b border-slate-700 hover:bg-slate-800 transition"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">
                        {EVENT_ICONS[event.event_type as keyof typeof EVENT_ICONS]}
                      </span>
                      <span className="text-sm">
                        {EVENT_LABELS[event.event_type as keyof typeof EVENT_LABELS]}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">{event.location}</td>
                  <td className="px-4 py-3">
                    <span
                      className="px-3 py-1 rounded font-semibold text-white text-sm"
                      style={{ backgroundColor: getSeverityColor(event.severity) }}
                    >
                      {event.severity}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {(event.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-400">
                    {getTimeAgo(event.detected_at)}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-400">
                    {event.data_source}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12 text-slate-400">
            <p>No events detected</p>
          </div>
        )}
      </div>

      <div className="text-sm text-slate-400 mt-4">
        Showing {sortedEvents.length} of {events.length} events
      </div>
    </div>
  )
}
