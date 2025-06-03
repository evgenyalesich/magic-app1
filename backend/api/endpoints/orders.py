from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def orders():
    return {"orders": "список заказов"}
