"""
Публичные эндпоинты для просмотра товаров (услуг).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.services.crud import product_crud
from backend.schemas.product import ProductOut

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get(
    "",
    response_model=list[ProductOut],
    summary="Список всех товаров (публично)",
)
async def list_products(db: AsyncSession = Depends(get_db)):
    """
    Вернуть список всех товаров/услуг.
    """
    return await product_crud.get_multi(db)

@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Детали товара по ID (публично)",
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить подробную информацию о товаре/услуге.
    """
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
