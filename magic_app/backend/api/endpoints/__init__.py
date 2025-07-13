from .auth import router as auth_router
from .products import router as products_router
from .orders import router as orders_router
from .messages import router as messages_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "products_router",
    "orders_router",
    "messages_router",
    "admin_router",
]
