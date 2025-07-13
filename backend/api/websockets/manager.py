# backend/api/websockets/manager.py

import json
import logging
from typing import List, Optional, Dict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from backend.models.message import Message
from backend.models.user import User

logger = logging.getLogger(__name__)


class SimpleConnectionManager:
    def __init__(self):
        # телеграм–ID → WebSocket
        self.user_connections: Dict[int, WebSocket] = {}
        self.admin_connections: Dict[int, WebSocket] = {}
        # WebSocket → телеграм–ID
        self.websocket_to_user: Dict[WebSocket, int] = {}

    async def connect_user(self, websocket: WebSocket, user_id: int):
        # НЕ вызываем здесь websocket.accept() — это делается в эндпоинте
        self.user_connections[user_id] = websocket
        self.websocket_to_user[websocket] = user_id
        logger.info(f"User connected: {user_id}")

    async def connect_admin(self, websocket: WebSocket, admin_id: int):
        # НЕ вызываем здесь websocket.accept()
        self.admin_connections[admin_id] = websocket
        self.websocket_to_user[websocket] = admin_id
        logger.info(f"Admin connected: {admin_id}")

    async def disconnect(self, websocket: WebSocket):
        """Удалить соединение (пользователь или админ)."""
        tg_id = self.websocket_to_user.pop(websocket, None)
        if tg_id is None:
            return
        if tg_id in self.user_connections:
            self.user_connections.pop(tg_id)
            logger.info(f"User disconnected: {tg_id}")
        if tg_id in self.admin_connections:
            self.admin_connections.pop(tg_id)
            logger.info(f"Admin disconnected: {tg_id}")

    async def send_to_user(self, user_id: int, data: dict) -> bool:
        """Отправить JSON конкретному пользователю (по telegram_id)."""
        ws = self.user_connections.get(user_id)
        if not ws:
            logger.warning(f"No WebSocket connection found for user {user_id}")
            logger.debug(f"Connected users: {list(self.user_connections.keys())}")
            return False
        payload = json.dumps(data)
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_text(payload)
                logger.info(f"✅ Message sent to user {user_id}: {data.get('type', 'unknown')}")
                return True
            else:
                logger.warning(f"WebSocket for user {user_id} is not connected (state: {ws.client_state})")
        except Exception as e:
            logger.error(f"Error sending to user {user_id}: {e}")
        # при ошибке — удаляем
        await self.disconnect(ws)
        return False

    async def send_to_admin(self, admin_id: int, data: dict) -> bool:
        """Отправить JSON конкретному администратору (по telegram_id)."""
        ws = self.admin_connections.get(admin_id)
        if not ws:
            return False
        payload = json.dumps(data)
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_text(payload)
                return True
        except Exception as e:
            logger.error(f"Error sending to admin {admin_id}: {e}")
        await self.disconnect(ws)
        return False

    async def send_to_all_admins(self, data: dict) -> int:
        """Броадкаст JSON всем подключённым администраторам."""
        sent = 0
        for aid in list(self.admin_connections.keys()):
            if await self.send_to_admin(aid, data):
                sent += 1
        return sent

    async def broadcast_to_admins(self, data: dict) -> int:
        """Alias for send_to_all_admins - броадкаст JSON всем подключённым администраторам."""
        return await self.send_to_all_admins(data)

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.user_connections

    def is_admin_online(self, admin_id: int) -> bool:
        return admin_id in self.admin_connections

    def get_stats(self) -> dict:
        return {
            "total_users_online": len(self.user_connections),
            "total_admins_online": len(self.admin_connections),
            "total_connections": len(self.user_connections) + len(self.admin_connections),
        }


# глобальный менеджер
manager = SimpleConnectionManager()


# ───────── Notifications ─────────

async def notify_new_message_to_admins(message: Message, sender_user_id: int):
    """
    Пользователь отправил новое сообщение — уведомляем всех админов.
    Фронт ожидает packet.type === "new_message" и packet.data.message.
    """
    payload = {
        "type": "new_message",
        "data": {
            "message": {
                "id": message.id,
                "user_id": message.user_id,
                "order_id": message.order_id,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "is_admin": False,
            }
        }
    }
    await manager.send_to_all_admins(payload)
    logger.debug(f"Admins notified of new user message from {sender_user_id}")


async def notify_admin_reply_to_user(message: Message, user_id: int):
    """
    Админ ответил пользователю — уведомляем его.
    Фронт ожидает packet.type === "message_replied" и packet.data с полями message_id, reply, replied_at.
    """
    payload = {
        "type": "message_replied",
        "data": {
            "message_id": message.id,
            "reply": message.reply,
            "replied_at": message.replied_at.isoformat() if message.replied_at else None,
        }
    }
    success = await manager.send_to_user(user_id, payload)
    if success:
        logger.info(f"✅ Пользователь {user_id} уведомлен об ответе админа на сообщение {message.id}")
    else:
        logger.warning(f"❌ Не удалось уведомить пользователя {user_id} об ответе админа")


# Остальные уведомления (typing, read, system) при желании можно оставить без изменений,
# главное, что новые/ответные сообщения теперь приходят в том формате, который ждёт фронт.
