import { useEffect, useRef } from 'react'

const DEFAULT_TRIAGE_WS_URL = 'ws://localhost:8080/ws/triage'

export function useTriageWebSocket(url = import.meta.env.VITE_TRIAGE_WS_URL ?? DEFAULT_TRIAGE_WS_URL) {
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const socket = new WebSocket(url)
    socketRef.current = socket

    socket.onopen = () => {
      console.info('Connected to the triage WebSocket')
    }

    socket.onmessage = (event) => {
      console.info('Triage WebSocket message:', event.data)
    }

    socket.onerror = (event) => {
      console.error('Triage WebSocket error:', event)
    }

    socket.onclose = (event) => {
      console.info('Triage WebSocket disconnected:', event.code, event.reason)
    }

    return () => {
      socket.close()
      socketRef.current = null
    }
  }, [url])

  return socketRef
}
