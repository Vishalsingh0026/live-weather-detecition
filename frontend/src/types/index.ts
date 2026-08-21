export interface Event {
  id: number
  event_type: 'extreme_rainfall' | 'flood_risk' | 'extreme_heat' | 'water_shortage' | 'severe_weather' | 'earthquake' | 'other'
  location: string
  latitude: number
  longitude: number
  severity: number
  confidence: number
  description?: string
  data_source: string
  is_active: boolean
  detected_at: string
  created_at: string
  updated_at: string
}

export interface Alert {
  id: number
  event_id: number
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  is_sent: boolean
  sent_at?: string
  created_at: string
  updated_at: string
}

export interface ResponsePlan {
  id: number
  event_id: number
  title: string
  description?: string
  recommended_actions: RecommendedAction[]
  resource_requirements: ResourceRequirement[]
  status: 'draft' | 'approved' | 'executing' | 'completed'
  priority_level: number
  estimated_impact?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface RecommendedAction {
  action: string
  priority: number
  estimated_duration_hours?: number
  assigned_to?: string
}

export interface ResourceRequirement {
  resource_type: string
  quantity: number
  priority: string
}

export interface DashboardMetrics {
  total_active_events: number
  critical_alerts: number
  high_severity_count: number
  average_risk_score: number
  last_updated: string
}

export interface WebSocketMessage {
  type: string
  data: Record<string, unknown>
  timestamp: string
  source: string
}
