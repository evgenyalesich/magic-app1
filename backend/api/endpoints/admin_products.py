"""
CRUD товаров (только для админов).

Роутер подключается в `admin.py` под префиксом **/products**,
поэтому здесь префикс не задаём.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
)
from backend.schemas.category import CategoryCreate  # схема для категории
from backend.services.crud import product_crud, category_crud  # импортируем оба CRUD

router = APIRouter()  # префикс берётся из admin.py


# ─────────────────────────────────────────────
# 1. Список товаров
# ─────────────────────────────────────────────
@router.get(
    "",
    response_model=list[ProductOut],
    summary="Список товаров",
)
async def list_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_multi(db)


# ─────────────────────────────────────────────
# 2. Создание товара (с автоматической категорией)
# ─────────────────────────────────────────────
@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить товар",
)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    # 1) Создаём новую категорию (имя можно взять из названия товара или константу)
    category = await category_crud.create(
        db,
        obj_in=CategoryCreate(name=payload.title)
    )
    # 2) Подготавливаем данные для товара, подставляя свежий category_id
    data = payload.dict()
    data["category_id"] = category.id
    # 3) Создаём товар
    return await product_crud.create(db, obj_in=ProductCreate(**data))


# ─────────────────────────────────────────────
# 3. Получить один товар
# ─────────────────────────────────────────────
@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Получить товар",
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# ─────────────────────────────────────────────
# 4. Обновление товара (с поддержкой смены категории)
# ─────────────────────────────────────────────
@router.put(
    "/{product_id}",
    response_model=ProductOut,
    summary="Обновить товар",
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    # 1) Проверяем, что товар существует
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # 2) Собираем только те поля, что пришли в запросе
    update_data = payload.dict(exclude_unset=True)

    # 3) Если меняем категорию — убедимся, что она есть
    if "category_id" in update_data:
        cat = await category_crud.get(db, update_data["category_id"])
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id={update_data['category_id']} not found",
            )

    # 4) Применяем обновление по правильной сигнатуре CRUDBase.update
    updated = await product_crud.update(
        db,
        product_id,
        obj_in=update_data,
    )
    return updated


# ─────────────────────────────────────────────
# 5. Удаление товара
# ─────────────────────────────────────────────
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
    response_class=Response,  # Код 204 не должен содержать тела
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await product_crud.remove(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
