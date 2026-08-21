import React, { useEffect, useState } from 'react'
import { apiClient } from './api/client'
import type { Event, Alert, DashboardMetrics, WebSocketMessage } from './types'
import { useWebSocket } from './hooks/useWebSocket'
import Dashboard from './components/Dashboard'
import EventsList from './components/EventsList'
import AlertsPanel from './components/AlertsPanel'
import ResponsePlansPanel from './components/ResponsePlansPanel'
import Navbar from './components/Navbar'

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'events' | 'alerts' | 'plans'>('dashboard')
  const [events, setEvents] = useState<Event[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { isConnected } = useWebSocket('/api/ws/events', {
    onMessage: (message: WebSocketMessage) => {
      console.log('Received WebSocket message:', message)

      // Handle real-time updates
      if (message.type === 'event_detected') {
        // Refresh events
        loadEvents()
      } else if (message.type === 'alert_triggered') {
        // Refresh alerts
        loadAlerts()
      }
    },
  })

  const loadEvents = async () => {
    try {
      const data = await apiClient.getEvents(0, 100)
      setEvents(data)
    } catch (err) {
      console.error('Failed to load events:', err)
      setError('Failed to load events')
    }
  }

  const loadAlerts = async () => {
    try {
      const data = await apiClient.getAlerts(0, 100)
      setAlerts(data)
    } catch (err) {
      console.error('Failed to load alerts:', err)
      setError('Failed to load alerts')
    }
  }

  const loadMetrics = async () => {
    try {
      const data = await apiClient.getEventsSummary()
      setMetrics({
        total_active_events: data.total_events || 0,
        critical_alerts: data.critical_events || 0,
        high_severity_count: data.high_severity_events || 0,
        average_risk_score: data.average_severity || 0,
        last_updated: new Date().toISOString(),
      })
    } catch (err) {
      console.error('Failed to load metrics:', err)
    }
  }

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)
        await Promise.all([loadEvents(), loadAlerts(), loadMetrics()])
      } catch (err) {
        console.error('Failed to load data:', err)
        setError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    loadData()

    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar isConnected={isConnected} />

      {error && (
        <div className="bg-red-600 text-white p-4 text-center">
          {error}
        </div>
      )}

      <div className="container mx-auto px-4 py-6">
        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6 border-b border-slate-700">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`pb-3 px-4 font-semibold transition-colors ${
              activeTab === 'dashboard'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`pb-3 px-4 font-semibold transition-colors ${
              activeTab === 'events'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Events ({events.length})
          </button>
          <button
            onClick={() => setActiveTab('alerts')}
            className={`pb-3 px-4 font-semibold transition-colors ${
              activeTab === 'alerts'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Alerts ({alerts.length})
          </button>
          <button
            onClick={() => setActiveTab('plans')}
            className={`pb-3 px-4 font-semibold transition-colors ${
              activeTab === 'plans'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Response Plans
          </button>
        </div>

        {/* Tab Content */}
        <div>
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
              <p className="mt-4">Loading dashboard...</p>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && metrics && <Dashboard metrics={metrics} events={events} />}
              {activeTab === 'events' && <EventsList events={events} />}
              {activeTab === 'alerts' && <AlertsPanel alerts={alerts} />}
              {activeTab === 'plans' && <ResponsePlansPanel />}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
