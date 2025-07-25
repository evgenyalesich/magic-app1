"""
ADMIN-panel API.

⚠️   Все маршруты защищены dependency-фильтром `admin_guard`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import admin_guard, get_db
from backend.schemas.admin import AdminMessageWithExtras
from backend.services.crud import admin_crud

# импорт под-роутеров (без префиксов!)
from .admin_products import router as admin_products_router
from .admin_messages import router as admin_messages_router

# ──────────────────────────────────────────────
# Главный роутер админки
# ──────────────────────────────────────────────
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_guard)],  # применяем ко ВСЕМ вложенным маршрутам
)

# ──────────────────────────────────────────────
# 1.  Приветственный энд-поинт
# ──────────────────────────────────────────────
@router.get("/", summary="Admin home")
async def admin_home(admin=Depends(admin_guard)):
    """Фронт запрашивает этот URL, чтобы убедиться, что токен = админ."""
    return {"message": f"Добро пожаловать в админ-панель, {admin.username}!"}

# ──────────────────────────────────────────────
# 2.  Дашборд
# ──────────────────────────────────────────────
@router.get(
    "/dashboard",
    response_model=AdminMessageWithExtras,
    summary="Dashboard metrics",
)
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
) -> AdminMessageWithExtras:
    stats = await admin_crud.get_admin_stats(db)
    return AdminMessageWithExtras(**stats)

# ──────────────────────────────────────────────
# 3.  Тематические под-роутеры
# ──────────────────────────────────────────────
#    prefix задаём здесь, чтобы итоговый путь был
#    /api/admin/products/*
router.include_router(
    admin_products_router,
    prefix="/products",
    tags=["Admin • Products"],
)

# ──────────────────────────────────────────────
#    prefix для истории переписки (/api/admin/messages)
# ──────────────────────────────────────────────
router.include_router(
    admin_messages_router,
    prefix="/messages",
    tags=["Admin • Messages"],
)

# ──────────────────────────────────────────────
#    prefix для отчёта (/api/admin/report)
# ──────────────────────────────────────────────
