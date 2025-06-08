import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("backend")

app = FastAPI(title="Magic App Backend")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Запрос: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(
        f"Ответ:  {request.method} {request.url} – статус {response.status_code}"
    )
    return response


# 1) CORS для вашего WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Подключаем API на /api/*
app.include_router(api_router, prefix="/api")


# 3) Статика:
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(static_dir):
    # 3.1) ассеты JS/CSS под /static/*
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(static_dir, "assets")),
        name="static-assets",
    )

    # 3.2) все остальные GET (кроме /api/*) — отдадим index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        from fastapi.responses import FileResponse

        return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
