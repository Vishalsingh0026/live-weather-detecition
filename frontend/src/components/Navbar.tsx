import React from 'react'

interface NavbarProps {
  isConnected: boolean
}

export default function Navbar({ isConnected }: NavbarProps) {
  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛡️</span>
            <h1 className="text-2xl font-bold text-blue-400">BharatResilience AI</h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-sm text-slate-400">
              Real-time Disaster Detection & Response Platform
            </div>

            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm font-semibold">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
