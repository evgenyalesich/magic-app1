from .manager import manager
# импортировать ws-эндпоинты откуда они лежат на самом деле:
from backend.api.ws import websocket_messages, websocket_notifications, websocket_health_check
