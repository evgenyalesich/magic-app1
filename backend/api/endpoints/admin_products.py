"""
CRUD товаров (только для админов).

Роутер подключается в `admin.py` под префиксом **/products**,
поэтому здесь префикс не задаём.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.schemas.product import ProductCreate, ProductUpdate, ProductOut
from backend.schemas.category import CategoryCreate
from backend.services.crud import product_crud, category_crud

router = APIRouter()


@router.get(
    "",
    response_model=list[ProductOut],
    summary="Список товаров",
)
async def list_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_multi(db)


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
    # Автосоздаём категорию по названию товара
    category = await category_crud.create(
        db,
        obj_in=CategoryCreate(name=payload.title),
    )
    # Вписываем её в данные для товара
    data = payload.dict()
    data["category_id"] = category.id
    # Создаём товар
    return await product_crud.create(db, obj_in=ProductCreate(**data))


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
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


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
    # Проверяем, что товар есть
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Берём лишь те поля, что пришли в запросе
    update_data = payload.dict(exclude_unset=True)

    # Если хотят сменить категорию — проверяем её наличие
    if "category_id" in update_data:
        cat = await category_crud.get(db, update_data["category_id"])
        if not cat:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id={update_data['category_id']} not found",
            )

    # Вызываем CRUD.update по id
    return await product_crud.update(
        db,
        product_id,
        obj_in=update_data,
    )


@router.delete(
    "/{product_id}",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Удалить товар",
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    # Проверяем, что товар есть
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Удаляем
    await product_crud.remove(db, product_id)

    # Возвращаем { "id": product_id }, чтобы фронтенд точно знал, что прошло OK
    return {"id": product_id}
