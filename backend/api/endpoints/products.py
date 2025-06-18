# endpoints/api/products.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.crud import product_crud
from backend.schemas.product import ProductCreate, ProductSchema
from backend.api.deps import db_session

router = APIRouter()

@router.get("/", response_model=list[ProductSchema], summary="List all products")
async def get_products(db: AsyncSession = Depends(db_session)):
    return await product_crud.get_all(db)


@router.post(
    "/",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(db_session),
):
    return await product_crud.create(db, product_in)


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    summary="Get a single product by ID",
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(db_session),
):
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put(
    "/{product_id}",
    response_model=ProductSchema,
    summary="Update a product by ID",
)
async def update_product(
    product_id: int,
    product_in: ProductCreate,
    db: AsyncSession = Depends(db_session),
):
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    return await product_crud.update(db, product_id, product_in)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product by ID",
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(db_session),
):
    existing = await product_crud.get(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    await product_crud.remove(db, product_id)
    return  # 204 No Content
