export const EVENT_TYPES = {
  EXTREME_RAINFALL: 'extreme_rainfall',
  FLOOD_RISK: 'flood_risk',
  EXTREME_HEAT: 'extreme_heat',
  WATER_SHORTAGE: 'water_shortage',
  SEVERE_WEATHER: 'severe_weather',
  EARTHQUAKE: 'earthquake',
  OTHER: 'other',
}

export const ALERT_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
}

export const SEVERITY_COLORS = {
  0: '#22c55e', // Low (green)
  1: '#eab308', // Medium (yellow)
  2: '#f97316', // High (orange)
  3: '#dc2626', // Critical (red)
}

export const SEVERITY_LABELS = {
  0: 'Low',
  1: 'Medium',
  2: 'High',
  3: 'Critical',
}

export const EVENT_ICONS = {
  extreme_rainfall: '🌧️',
  flood_risk: '🌊',
  extreme_heat: '🌡️',
  water_shortage: '💧',
  severe_weather: '🌪️',
  earthquake: '📍',
  other: '⚠️',
}

export const EVENT_LABELS = {
  extreme_rainfall: 'Extreme Rainfall',
  flood_risk: 'Flood Risk',
  extreme_heat: 'Extreme Heat',
  water_shortage: 'Water Shortage',
  severe_weather: 'Severe Weather',
  earthquake: 'Earthquake',
  other: 'Other Hazard',
}

export function getSeverityLevel(score: number) {
  if (score >= 85) return 3 // Critical
  if (score >= 70) return 2 // High
  if (score >= 50) return 1 // Medium
  return 0 // Low
}

export function getSeverityColor(score: number) {
  const level = getSeverityLevel(score)
  return SEVERITY_COLORS[level as keyof typeof SEVERITY_COLORS]
}

export function getSeverityLabel(score: number) {
  const level = getSeverityLevel(score)
  return SEVERITY_LABELS[level as keyof typeof SEVERITY_LABELS]
}

export function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleString()
}

export function formatTime(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleTimeString()
}

export function getTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}
