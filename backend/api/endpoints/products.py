from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.crud import product_crud
from backend.schemas.product import ProductCreate, ProductSchema
from backend.api.deps import get_db

router = APIRouter()


@router.get("/", response_model=list[ProductSchema])
async def get_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_all(db)


@router.post("/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_crud.create(db, product)


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product
