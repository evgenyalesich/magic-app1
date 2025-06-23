# backend/api/endpoints/ws_endpoints.py
from fastapi import APIRouter, WebSocket
from backend.api.ws import manager

router = APIRouter()

@router.websocket("/ws/messages")
async def websocket_messages(ws: WebSocket):
    """
    Клиент подписывается на channel=new_message,
    и будет получать JSON-строки MessageOut
    """
    await manager.connect(ws)
    try:
        while True:
            # ждём от клиента keep-alive, но можно без чтения
            await ws.receive_text()
    finally:
        await manager.disconnect(ws)
