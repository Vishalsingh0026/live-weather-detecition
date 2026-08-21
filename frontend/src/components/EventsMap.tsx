import React, { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { Event } from '../types'
import { EVENT_ICONS, getSeverityColor } from '../utils/constants'

interface EventsMapProps {
  events: Event[]
}

// Fix Leaflet marker icons
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

L.Marker.prototype.setIcon(DefaultIcon)

export default function EventsMap({ events }: EventsMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.Marker[]>([])

  useEffect(() => {
    if (!mapContainerRef.current) return

    // Initialize map
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView([20.5937, 78.9629], 5)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 2,
      }).addTo(mapRef.current)
    }

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove())
    markersRef.current = []

    // Add event markers
    events.forEach(event => {
      if (mapRef.current) {
        const markerColor = getSeverityColor(event.severity)
        const severity = Math.max(0, Math.min(100, event.severity))

        // Create custom marker with HTML
        const markerHtml = `
          <div style="
            background-color: ${markerColor};
            color: white;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-weight: bold;
            font-size: 14px;
          ">
            ${severity}
          </div>
        `

        const icon = L.divIcon({
          html: markerHtml,
          iconSize: [35, 35],
          className: 'custom-marker',
        })

        const marker = L.marker([event.latitude, event.longitude], { icon })
          .bindPopup(
            `<div style="width: 200px">
              <h4 style="font-weight: bold; margin-bottom: 5px;">${EVENT_ICONS[event.event_type as keyof typeof EVENT_ICONS]} ${event.event_type.replace('_', ' ')}</h4>
              <p><strong>Location:</strong> ${event.location}</p>
              <p><strong>Severity:</strong> ${event.severity}/100</p>
              <p><strong>Confidence:</strong> ${(event.confidence * 100).toFixed(0)}%</p>
              <p><strong>Time:</strong> ${new Date(event.detected_at).toLocaleTimeString()}</p>
              ${event.description ? `<p><strong>Description:</strong> ${event.description}</p>` : ''}
            </div>`,
            {
              maxWidth: 250,
            }
          )
          .addTo(mapRef.current)

        markersRef.current.push(marker)
      }
    })

    // Fit bounds if events exist
    if (events.length > 0 && mapRef.current) {
      const bounds = L.latLngBounds(
        events.map(e => [e.latitude, e.longitude] as [number, number])
      )
      mapRef.current.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 })
    }
  }, [events])

  return (
    <div ref={mapContainerRef} style={{ width: '100%', height: '400px' }} />
  )
}
