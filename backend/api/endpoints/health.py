# backend/api/endpoints/health.py
from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])

@router.get("/", include_in_schema=False)
async def health(request: Request):
    """
    Простейший health-check:
    • всегда отдаёт 200 OK
    • сообщает, где доступны OpenAPI/Docs у того приложения, в которое он «вмонтирован».
    """
    app = request.app
    return {
        "openapi": app.openapi_url,
        "docs":    app.docs_url,
        "redoc":   app.redoc_url,
    }
