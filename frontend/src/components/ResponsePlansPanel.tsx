import React, { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import type { ResponsePlan } from '../types'
import { getSeverityColor } from '../utils/constants'

type PlanStatus = ResponsePlan['status']

const STATUS_ORDER: PlanStatus[] = ['draft', 'approved', 'executing', 'completed']

const STATUS_COLORS: Record<PlanStatus, string> = {
  draft: 'bg-slate-700',
  approved: 'bg-blue-700',
  executing: 'bg-orange-700',
  completed: 'bg-green-700',
}

const getNextStatus = (status: PlanStatus): PlanStatus | null => {
  const nextIndex = STATUS_ORDER.indexOf(status) + 1
  return STATUS_ORDER[nextIndex] ?? null
}

export default function ResponsePlansPanel() {
  const [plans, setPlans] = useState<ResponsePlan[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [expandedPlanId, setExpandedPlanId] = useState<number | null>(null)
  const [updatingPlanId, setUpdatingPlanId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadPlans = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getResponsePlans(0, 100)
        setPlans(data)
      } catch (error) {
        console.error('Failed to load response plans:', error)
        setError('Unable to load response plans.')
      } finally {
        setLoading(false)
      }
    }

    loadPlans()
  }, [])

  const updateStatus = async (plan: ResponsePlan) => {
    const nextStatus = getNextStatus(plan.status)
    if (!nextStatus) return

    try {
      setError(null)
      setUpdatingPlanId(plan.id)
      const updatedPlan = await apiClient.updatePlanStatus(plan.id, nextStatus)
      setPlans(currentPlans =>
        currentPlans.map(currentPlan =>
          currentPlan.id === updatedPlan.id ? updatedPlan : currentPlan
        )
      )
    } catch (error) {
      console.error('Failed to update response plan:', error)
      setError(`Unable to move plan #${plan.id} to ${nextStatus}.`)
    } finally {
      setUpdatingPlanId(null)
    }
  }

  const filteredPlans = plans.filter(
    plan => filter === 'all' || plan.status === filter
  )

  const stats = {
    total: plans.length,
    draft: plans.filter(p => p.status === 'draft').length,
    approved: plans.filter(p => p.status === 'approved').length,
    executing: plans.filter(p => p.status === 'executing').length,
    completed: plans.filter(p => p.status === 'completed').length,
  }

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Object.entries(stats).map(([key, value]) => (
          <div key={key} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <p className="text-slate-400 text-xs uppercase mb-2">{key}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          All Plans
        </button>
        <button
          onClick={() => setFilter('draft')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'draft'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Draft
        </button>
        <button
          onClick={() => setFilter('approved')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'approved'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Approved
        </button>
        <button
          onClick={() => setFilter('executing')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'executing'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Executing
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded text-sm font-semibold transition ${
            filter === 'completed'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Completed
        </button>
      </div>

      {error && (
        <div role="alert" className="rounded-lg border border-red-800 bg-red-950 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      {/* Plans List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          <p className="mt-2">Loading response plans...</p>
        </div>
      ) : filteredPlans.length > 0 ? (
        <div className="space-y-4">
          {filteredPlans.map(plan => {
            const nextStatus = getNextStatus(plan.status)
            const isExpanded = expandedPlanId === plan.id

            return (
            <div key={plan.id} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{plan.title}</h3>
                  <p className="text-sm text-slate-400 mt-1">{plan.description}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 rounded text-sm font-semibold text-white ${STATUS_COLORS[plan.status]}`}
                  >
                    {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                  </span>
                  <span
                    className="px-3 py-1 rounded text-sm font-semibold text-white"
                    style={{ backgroundColor: getSeverityColor(plan.priority_level) }}
                  >
                    Priority: {plan.priority_level}
                  </span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 border-b border-slate-700 pb-4 text-sm text-slate-400">
                <span>Event #{plan.event_id}</span>
                <span>{plan.recommended_actions.length} actions</span>
                <span>{plan.resource_requirements.length} resource types</span>
                <button
                  type="button"
                  onClick={() => setExpandedPlanId(isExpanded ? null : plan.id)}
                  className="ml-auto rounded bg-slate-700 px-3 py-2 font-semibold text-slate-200 hover:bg-slate-600"
                  aria-expanded={isExpanded}
                >
                  {isExpanded ? 'Hide details' : 'View details'}
                </button>
                {nextStatus && (
                  <button
                    type="button"
                    onClick={() => updateStatus(plan)}
                    disabled={updatingPlanId === plan.id}
                    className="rounded bg-blue-600 px-3 py-2 font-semibold text-white hover:bg-blue-500 disabled:cursor-wait disabled:opacity-60"
                  >
                    {updatingPlanId === plan.id ? 'Updating...' : `Move to ${nextStatus}`}
                  </button>
                )}
              </div>

              {isExpanded && <>
              {/* Recommended Actions */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold mb-2 text-blue-400">
                  📋 Recommended Actions
                </h4>
                <div className="space-y-2">
                  {plan.recommended_actions.map((action, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 text-sm bg-slate-900 p-3 rounded"
                    >
                      <span className="text-slate-400">{idx + 1}.</span>
                      <div>
                        <p className="font-semibold">{action.action}</p>
                        <div className="text-xs text-slate-400 mt-1 flex gap-4">
                          <span>Priority: {action.priority}</span>
                          {action.estimated_duration_hours && (
                            <span>Duration: ~{action.estimated_duration_hours}h</span>
                          )}
                          {action.assigned_to && (
                            <span>Assigned to: {action.assigned_to}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Resource Requirements */}
              <div>
                <h4 className="text-sm font-semibold mb-2 text-green-400">
                  🔧 Resources Needed
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {plan.resource_requirements.map((resource, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900 p-3 rounded border border-slate-700 text-sm"
                    >
                      <p className="font-semibold">{resource.resource_type}</p>
                      <p className="text-slate-400">
                        Qty: <span className="text-white font-bold">{resource.quantity}</span>
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Priority: {resource.priority}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Impact Estimates */}
              {plan.estimated_impact && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <h4 className="text-sm font-semibold mb-2 text-yellow-400">
                    📊 Estimated Impact
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    {Object.entries(plan.estimated_impact).map(([key, value]) => (
                      <div key={key} className="text-slate-300">
                        <p className="text-slate-400 text-xs mb-1">{key}</p>
                        <p className="font-semibold">{String(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              </>}
            </div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-slate-400">
          <p>No response plans in this category</p>
        </div>
      )}
    </div>
  )
}
