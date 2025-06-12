from fastapi import APIRouter
from backend.main import app

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "openapi": app.openapi_url,
        "docs": app.docs_url,
        "redoc": app.redoc_url,
    }
