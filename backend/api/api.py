"""
Главный router приложения. Собирает все энд-пойнты /api/**.
"""
from fastapi import APIRouter

from backend.api.endpoints.health     import router as health_router
from backend.api.endpoints.auth       import router as auth_router
from backend.api.endpoints.products   import router as products_router
from backend.api.endpoints.orders     import router as orders_router
from backend.api.endpoints.messages   import router as messages_router
from backend.api.endpoints.categories import router as categories_router
from backend.api.endpoints.users      import router as users_router
from backend.api.endpoints.admin      import router as admin_router

api_router = APIRouter()

# ───────── системные
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router,   prefix="/auth",   tags=["Auth"])

# ───────── бизнес-сущности
api_router.include_router(products_router,    tags=["Products"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(orders_router,     prefix="/orders",     tags=["Orders"])
api_router.include_router(messages_router,   prefix="/messages",   tags=["Messages"])
api_router.include_router(users_router,      prefix="/users",      tags=["Users"])
# ───────── админ-панель
# prefix НЕ указываем — он уже есть внутри admin_router
api_router.include_router(admin_router)      # /api/admin/**
