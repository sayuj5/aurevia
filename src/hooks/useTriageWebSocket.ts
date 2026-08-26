import { useEffect, useRef, useState } from 'react'
import { useStore } from '../store/useStore'

const DEFAULT_TRIAGE_WS_URL = 'ws://localhost:8080/ws/triage'

export type TriageConnectionState = 'connecting' | 'live' | 'offline'

interface RiskEscalationPayload {
  caseId: string
  score: number
  tier?: 'low' | 'moderate' | 'high' | 'critical'
}

interface TriageSocketMessage {
  type: 'RISK_ESCALATION' | 'EMERGENCY_ALERT'
  payload: RiskEscalationPayload | Record<string, unknown>
}

// Connects to the FastAPI real-time hub (/ws/triage). On a RISK_ESCALATION
// message it updates the shared case store directly, so the Dashboard's
// score/tier and Case Management's row update live without a page refresh.
// Falls back to "offline" gracefully if the backend isn't running yet —
// expected during hackathon dev — the dashboard just keeps showing the
// last fetched data either way.
export function useTriageWebSocket(url = import.meta.env.VITE_TRIAGE_WS_URL ?? DEFAULT_TRIAGE_WS_URL) {
  const [status, setStatus] = useState<TriageConnectionState>('connecting')
  const socketRef = useRef<WebSocket | null>(null)
  const updateCaseRisk = useStore((s) => s.updateCaseRisk)
  const addLiveNotification = useStore((s) => s.addLiveNotification)

  useEffect(() => {
    let socket: WebSocket
    try {
      socket = new WebSocket(url)
      socketRef.current = socket

      socket.onopen = () => setStatus('live')

      socket.onmessage = (event) => {
        try {
          const msg: TriageSocketMessage = JSON.parse(event.data)
          if (msg.type === 'RISK_ESCALATION') {
            const { caseId, score, tier } = msg.payload as RiskEscalationPayload
            updateCaseRisk(caseId, score, tier)
          } else if (msg.type === 'EMERGENCY_ALERT') {
            addLiveNotification(msg.payload as never)
          }
        } catch {
          // Malformed payload — ignore rather than crash the dashboard
        }
      }

      socket.onerror = () => setStatus('offline')
      socket.onclose = () => setStatus('offline')
    } catch {
      setStatus('offline')
    }

    return () => {
      socketRef.current?.close()
      socketRef.current = null
    }
  }, [url, updateCaseRisk, addLiveNotification])

  return status
}
