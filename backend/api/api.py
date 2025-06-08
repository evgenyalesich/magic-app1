from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.products import router as products_router
from .endpoints.orders import router as orders_router
from .endpoints.messages import router as messages_router
from .endpoints.admin import router as admin_router

api_router = APIRouter()

# Auth endpoints: login, profile, user lookup and bot registration
# Все эндпоинты из auth_router, включая /bot-register, будут доступны по /api/auth/*
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# Products endpoints: GET /api/products, GET /api/products/{id}
api_router.include_router(products_router, prefix="/products", tags=["Products"])
# Orders endpoints: POST /api/orders
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
# Chat endpoints: GET/POST under /api/chat
api_router.include_router(messages_router, prefix="/chat", tags=["Chat"])
# Admin endpoints: префикс задается внутри admin_router
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
