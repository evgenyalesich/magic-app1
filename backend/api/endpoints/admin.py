from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.services.crud import user_crud, order_crud, message_crud
from backend.schemas.admin import AdminStats
from backend.api.endpoints.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/", response_model=dict)
async def admin_home(user = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return {"message": f"Добро пожаловать в админ‑панель, {user.username}"}


@router.get("/dashboard", response_model=AdminStats)
async def get_admin_dashboard(
    db: AsyncSession = Depends(db_session),
    user = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    total_users     = await user_crud.count_users(db)
    total_orders    = await order_crud.count_orders(db)
    total_revenue   = (await order_crud.calculate_total_revenue(db)) or 0.0
    unread_messages = await message_crud.count_unread_messages(db)

    return AdminStats(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=total_revenue,
        unread_messages=unread_messages
    )
