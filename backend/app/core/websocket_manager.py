"""
WebSocket Connection Manager for Real-Time Fleet Streaming.
Broadcasts live vehicle position updates, speed alerts, and telemetry events to connected clients.
"""
from typing import List, Dict, Any
from fastapi import WebSocket
import json


class WebSocketManager:
    """Manager for active WebSocket client connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept connection and add to active pool."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove disconnected client from active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast payload to all connected clients."""
        dead_connections: List[WebSocket] = []
        payload_str = json.dumps(message, default=str)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(payload_str)
            except Exception:
                dead_connections.append(connection)

        # Cleanup dead connections
        for dead in dead_connections:
            self.disconnect(dead)


# Global Singleton Instance
ws_manager = WebSocketManager()
