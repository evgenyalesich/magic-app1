# backend/core/notify.py
import asyncio
import asyncpg
import os
from backend.core.config import DATABASE_URL
from backend.api.ws import manager  # см. ниже

async def pg_listener():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.add_listener("new_message", handle)
    # «висим» вечно
    await asyncio.Future()

def handle(connection, pid, channel, payload):
    # payload — это JSON строки модели MessageOut
    asyncio.create_task(manager.broadcast_json(payload))
