# backend/api/api.py
"""
Главный router приложения. Собирает все энд-пойнты /api/**.
"""
from fastapi import APIRouter

# системные
from backend.api.endpoints.health     import router as health_router
from backend.api.endpoints.auth       import router as auth_router

# бизнес-сущности
from backend.api.endpoints.products   import router as products_router
from backend.api.endpoints.categories import router as categories_router
from backend.api.endpoints.orders     import router as orders_router
from backend.api.endpoints.messages   import router as messages_router
from backend.api.endpoints.admin_messages import router as  admin_messages_router

# оплата
from backend.api.endpoints.payments   import router as payments_router

# WebSocket
from backend.api.endpoints.ws_endpoints import router as ws_router

# админ-панель
from backend.api.endpoints.admin      import router as admin_router


api_router = APIRouter()

# ───────── системные
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router,   prefix="/auth",   tags=["Auth"])

# ───────── бизнес-сущности
api_router.include_router(products_router,    tags=["Products"])
api_router.include_router(orders_router,       tags=["Orders"])
api_router.include_router(messages_router)         # /api/messages/**
api_router.include_router(admin_messages_router)
# ───────── оплата
api_router.include_router(payments_router)

# ───────── WebSocket-канал для пушей сообщений
api_router.include_router(ws_router)

# ───────── админ-панель
# префикс (/admin/…) уже зашит внутри admin_router
api_router.include_router(admin_router)
