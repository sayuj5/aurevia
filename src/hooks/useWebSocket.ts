import { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';

export function useWebSocket(url: string = 'ws://localhost:8000/ws/triage') {
  // Grab our new functions from the store we just made
  const updateCaseRisk = useStore((state) => state.updateCaseRisk);
  const addLiveNotification = useStore((state) => state.addLiveNotification);
  
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Open the connection to the backend
    ws.current = new WebSocket(url);

    ws.current.onopen = () => console.log('Connected to Triage Hub');

    // Listen for incoming messages
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Route the message to the right Zustand function
      if (data.type === 'RISK_ESCALATION') {
         updateCaseRisk(data.payload.caseId, data.payload.score);
      } else if (data.type === 'EMERGENCY_ALERT') {
         addLiveNotification(data.payload);
      }
    };

    ws.current.onclose = () => console.log('Disconnected from Triage Hub');

    // Cleanup when the component unmounts
    return () => {
      ws.current?.close();
    };
  }, [url, updateCaseRisk, addLiveNotification]);

  return ws.current;
}