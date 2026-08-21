import { useEffect, useRef, useState } from 'react'
import type { WebSocketMessage } from '../types'

export interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  autoReconnect?: boolean
  reconnectDelay?: number
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const reconnectTimeoutRef = useRef<number | null>(null)

  const { onMessage, onConnect, onDisconnect, autoReconnect = true, reconnectDelay = 3000 } = options

  useEffect(() => {
    const wsUrl = url.startsWith('ws') ? url : `ws://${window.location.host}${url}`

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          onConnect?.()
        }

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data) as WebSocketMessage
            onMessage?.(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          onDisconnect?.()

          if (autoReconnect) {
            reconnectTimeoutRef.current = window.setTimeout(connect, reconnectDelay)
          }
        }

        wsRef.current = ws
      } catch (error) {
        console.error('Failed to create WebSocket:', error)
        if (autoReconnect) {
          reconnectTimeoutRef.current = window.setTimeout(connect, reconnectDelay)
        }
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      wsRef.current?.close()
    }
  }, [url])

  const send = (data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }

  return { isConnected, send }
}
