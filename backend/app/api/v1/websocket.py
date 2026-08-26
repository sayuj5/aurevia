import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.messaging.consumer import listen_to_channel

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

async def handle_triage_event(message_data: dict):
    await manager.broadcast(message_data)

async def start_websocket_listener():
    asyncio.create_task(listen_to_channel("triage_events", handle_triage_event))

@router.websocket("/ws/triage")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)