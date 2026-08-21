import axios, { AxiosInstance } from 'axios'
import type { Event, Alert, ResponsePlan } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Events
  async getEvents(skip = 0, limit = 50) {
    const response = await this.client.get<Event[]>('/events', {
      params: { skip, limit },
    })
    return response.data
  }

  async getEvent(id: number) {
    const response = await this.client.get<Event>(`/events/${id}`)
    return response.data
  }

  async createEvent(event: Partial<Event>) {
    const response = await this.client.post<Event>('/events', event)
    return response.data
  }

  async getEventsSummary() {
    const response = await this.client.get('/events/stats/summary')
    return response.data
  }

  // Alerts
  async getAlerts(skip = 0, limit = 50) {
    const response = await this.client.get<Alert[]>('/alerts', {
      params: { skip, limit },
    })
    return response.data
  }

  async getAlert(id: number) {
    const response = await this.client.get<Alert>(`/alerts/${id}`)
    return response.data
  }

  async createAlert(alert: Partial<Alert>) {
    const response = await this.client.post<Alert>('/alerts', alert)
    return response.data
  }

  async sendAlert(id: number) {
    const response = await this.client.put<Alert>(`/alerts/${id}/send`)
    return response.data
  }

  async getCriticalAlerts() {
    const response = await this.client.get('/alerts/stats/critical')
    return response.data
  }

  // Response Plans
  async getResponsePlans(skip = 0, limit = 50) {
    const response = await this.client.get<ResponsePlan[]>('/response-plans', {
      params: { skip, limit },
    })
    return response.data
  }

  async getResponsePlan(id: number) {
    const response = await this.client.get<ResponsePlan>(`/response-plans/${id}`)
    return response.data
  }

  async createResponsePlan(plan: Partial<ResponsePlan>) {
    const response = await this.client.post<ResponsePlan>('/response-plans', plan)
    return response.data
  }

  async updatePlanStatus(id: number, status: string) {
    const response = await this.client.put<ResponsePlan>(
      `/response-plans/${id}/status`,
      { new_status: status }
    )
    return response.data
  }

  async getPlanByEvent(eventId: number) {
    const response = await this.client.get<ResponsePlan>(
      `/response-plans/event/${eventId}`
    )
    return response.data
  }

  // Data Feeds
  async getDataFeeds() {
    const response = await this.client.get('/data-feeds')
    return response.data
  }

  async getFeedHealth() {
    const response = await this.client.get('/data-feeds/stats/feed-health')
    return response.data
  }

  // Health
  async getHealth() {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const apiClient = new APIClient()
