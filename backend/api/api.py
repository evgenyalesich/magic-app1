from fastapi import APIRouter
from .endpoints.auth     import router as auth_router
from .endpoints.products import router as products_router
from .endpoints.orders   import router as orders_router
from .endpoints.messages import router as messages_router
from .endpoints.admin    import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router,     prefix="/auth",     tags=["Auth"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(orders_router,   prefix="/orders",   tags=["Orders"])
api_router.include_router(messages_router, prefix="/messages", tags=["Messages"])
api_router.include_router(admin_router)  # префикс /admin уже внутри router
