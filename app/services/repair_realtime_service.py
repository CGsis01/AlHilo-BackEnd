from dataclasses import dataclass
from typing import Dict, Any, Optional
from fastapi import WebSocket

@dataclass
class RepairRealtimeConnection:
    user_id: str
    store_id: Optional[str]

class RepairRealtimeBroker:
    def __init__(self) -> None:
        self._connections: Dict[WebSocket, RepairRealtimeConnection] = {}

    async def connect(self, websocket: WebSocket, user_id: str, store_id: Optional[str] = None) -> None:
        await websocket.accept()
        self._connections[websocket] = RepairRealtimeConnection(user_id=user_id, store_id=store_id)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.pop(websocket, None)

    async def broadcast(self, event: Dict[str, Any], store_id: Optional[str] = None) -> None:
        stale_connections = []

        for websocket, connection in list(self._connections.items()):
            if store_id and connection.store_id != store_id:
                continue

            try:
                await websocket.send_json(event)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(websocket)

repair_realtime_broker = RepairRealtimeBroker()
