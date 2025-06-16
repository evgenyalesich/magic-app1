# backend/main.py
import os
import logging
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.api import api_router
from backend.core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# Настройка логирования на основании переменной окружения LOG_LEVEL
log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=numeric_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend")
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Magic App Backend")


# ────────────────────────── middleware: логирование ─────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("Incoming request: %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Error handling request %s", request.url.path)
        raise
    logger.debug(
        "Completed request: %s %s → %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


# ─────────────────────────────── CORS ───────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ────────────── REST-API (всё под /api) ─────────────────────────────────────
app.include_router(api_router, prefix="/api")


# ───────────────────── Поиск каталога dist  ────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
candidates = [
    project_root / "frontend" / "dist",  # стандартно: frontend/dist
    project_root / "dist",               # альтернативно
]
dist_dir = next((p for p in candidates if p.is_dir()), None)

if dist_dir:
    logger.info("📦 Front-end mounted from %s", dist_dir)

    # 1) статические файлы Vite — лежат в /assets
    app.mount(
        "/assets",
        StaticFiles(directory=dist_dir / "assets", html=False),
        name="assets",
    )

    # 2) SPA-fallback для React Router
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str):
        # если это не GET или путь API/Assets, 404
        if request.method != "GET" or request.url.path.startswith(("/api", "/assets")):
            raise HTTPException(status_code=404)
        return FileResponse(dist_dir / "index.html")
else:
    logger.warning(
        "❗ dist каталога не найдено — фронт не будет отдаваться (искали в %s)",
        candidates,
    )


# ───────────────────────────── health-check ────────────────────────────────
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
