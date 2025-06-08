import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend")

app = FastAPI(title="Magic App Backend")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Запрос: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Ошибка обработки запроса {request.url.path}: {exc}")
        raise
    logger.info(f"Ответ: {request.method} {request.url.path} → {response.status_code}")
    return response


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Все эндпойнты под /api
app.include_router(api_router, prefix="/api")

# Если собран фронтенд
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(static_dir):
    # 1) Статика на /static
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # 2) SPA-fallback: любой GET, не /api и не /static → index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str):
        if request.method != "GET" or request.url.path.startswith(("/api", "/static")):
            raise HTTPException(404)
        return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
