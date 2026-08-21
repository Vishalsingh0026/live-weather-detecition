import React from 'react'
import { getSeverityColor, getSeverityLabel, getSeverityLevel } from '../utils/constants'

interface RiskScoreGaugeProps {
  score: number
}

export default function RiskScoreGauge({ score }: RiskScoreGaugeProps) {
  const clampedScore = Math.max(0, Math.min(100, score))
  const angle = (clampedScore / 100) * 180 - 90
  const level = getSeverityLevel(clampedScore)
  const color = getSeverityColor(clampedScore)

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-24 flex items-center justify-center">
        {/* Gauge background */}
        <svg width="200" height="100" viewBox="0 0 200 100" className="absolute">
          {/* Gauge arc background */}
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22c55e" />
              <stop offset="33%" stopColor="#eab308" />
              <stop offset="67%" stopColor="#f97316" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>

          {/* Background arc */}
          <path
            d="M 20 80 A 60 60 0 0 1 180 80"
            fill="none"
            stroke="#334155"
            strokeWidth="8"
            strokeLinecap="round"
          />

          {/* Colored arc */}
          <path
            d="M 20 80 A 60 60 0 0 1 180 80"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(clampedScore / 100) * (Math.PI * 120)} ${Math.PI * 120}`}
          />

          {/* Center circle */}
          <circle cx="100" cy="80" r="8" fill="#1e293b" />

          {/* Needle */}
          <line
            x1="100"
            y1="80"
            x2={100 + Math.cos((angle * Math.PI) / 180) * 50}
            y2={80 + Math.sin((angle * Math.PI) / 180) * 50}
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Labels */}
          <text x="25" y="95" fontSize="10" fill="#64748b" textAnchor="middle">
            Low
          </text>
          <text x="100" y="15" fontSize="10" fill="#64748b" textAnchor="middle">
            Critical
          </text>
          <text x="175" y="95" fontSize="10" fill="#64748b" textAnchor="middle">
            High
          </text>
        </svg>

        {/* Score display */}
        <div className="absolute flex flex-col items-center">
          <span className="text-4xl font-bold" style={{ color }}>
            {clampedScore.toFixed(0)}
          </span>
          <span className="text-xs text-slate-400 mt-1">Risk Score</span>
        </div>
      </div>

      {/* Severity label */}
      <div className="mt-4 text-center">
        <p
          className="text-2xl font-bold"
          style={{ color }}
        >
          {getSeverityLabel(clampedScore)}
        </p>
        <p className="text-xs text-slate-400 mt-2">
          {clampedScore >= 85 && 'Immediate action required'}
          {clampedScore < 85 && clampedScore >= 70 && 'Prepare emergency response'}
          {clampedScore < 70 && clampedScore >= 50 && 'Monitor closely'}
          {clampedScore < 50 && 'Routine monitoring'}
        </p>
      </div>
    </div>
  )
}
