# backend/api/ws.py
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    async def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast_json(self, data: str):
        # data уже сериализованный JSON
        for ws in list(self.active):
            try:
                await ws.send_text(data)
            except:
                await self.disconnect(ws)

manager = ConnectionManager()
