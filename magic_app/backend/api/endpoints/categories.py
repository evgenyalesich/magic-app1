from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.category import CategoryCreate, CategoryRead
from backend.services.crud import category_crud
from backend.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    cat_in: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    return await category_crud.create(db, cat_in)

@router.get("/", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await category_crud.get_multi(db)
