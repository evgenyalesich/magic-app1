import logging
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.api.api import api_router
from backend.core.config import settings

# Настройка логирования
log_level_name = settings.LOG_LEVEL.upper()
numeric_level = getattr(logging, log_level_name, logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s"
)
logging.basicConfig(
    level=numeric_level,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend")
middleware_logger = logging.getLogger("middleware")
cors_logger = logging.getLogger("cors")
security_logger = logging.getLogger("security")

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

app = FastAPI(title="Magic App Backend")

# Добавляем TrustedHost middleware для безопасности
allowed_hosts = ["*"]
if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
    allowed_hosts = settings.ALLOWED_HOSTS
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Улучшенный middleware для логирования и мониторинга
@app.middleware("http")
async def enhanced_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    request.state.request_id = request_id
    middleware_logger.info("🔄 [%s] START: %s %s | IP: %s | UA: %s", request_id, request.method, request.url.path, client_ip, user_agent[:100])
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        status_emoji, log_level = "✅", middleware_logger.info
        if response.status_code >= 500:
            status_emoji, log_level = "💥", middleware_logger.error
        elif response.status_code >= 400:
            status_emoji, log_level = "⚠️", middleware_logger.warning
        log_level("%s [%s] END: %s %s → %s | %.3fs", status_emoji, request_id, request.method, request.url.path, response.status_code, process_time)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        return response
    except Exception as e:
        process_time = time.time() - start_time
        middleware_logger.error("❌ [%s] ERROR: %s %s | Exception: %s | %.3fs | IP: %s", request_id, request.method, request.url.path, str(e), process_time, client_ip)
        middleware_logger.exception("🔍 [%s] Full traceback for %s %s:", request_id, request.method, request.url.path)
        raise

# Список доменов Telegram для CORS и CSP
telegram_origins = [
    "https://web.telegram.org",
    "https://webk.telegram.org",
    "https://webz.telegram.org",
    "https://telegram.org",
    "https://core.telegram.org",
]

# Middleware для безопасности и мониторинга подозрительной активности
@app.middleware("http")
async def security_monitoring_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    suspicious_paths = ["/admin", "/.env", "/wp-admin", "/phpmyadmin", "/config", "/.git", "/backup", "/test", "/debug", "/console", "/api/v1/admin", "/swagger", "/docs", "/redoc"]
    suspicious_user_agents = ["sqlmap", "nikto", "nmap", "masscan", "burp", "owasp"]
    if any(path in request.url.path.lower() for path in suspicious_paths):
        security_logger.warning("🚨 SUSPICIOUS_PATH: %s requested %s %s", client_ip, request.method, request.url.path)
    if any(agent.lower() in user_agent.lower() for agent in suspicious_user_agents):
        security_logger.warning("🚨 SUSPICIOUS_UA: %s with User-Agent: %s", client_ip, user_agent)

    response = await call_next(request)

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    # Устанавливаем стандартные заголовки безопасности
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Заменяем строгий X-Frame-Options на гибкий Content-Security-Policy,
    # чтобы разрешить встраивание приложения в клиентах Telegram.
    allowed_ancestors = " ".join(["'self'"] + telegram_origins)
    response.headers["Content-Security-Policy"] = f"frame-ancestors {allowed_ancestors};"
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

# Настройка CORS для работы с Telegram и веб-приложениями
# Надежно получаем настройки, чтобы избежать TypeError
frontend_origins = []
if hasattr(settings, 'FRONTEND_ORIGIN') and settings.FRONTEND_ORIGIN:
    origin_setting = settings.FRONTEND_ORIGIN
    if isinstance(origin_setting, list):
        frontend_origins = [str(o) for o in origin_setting if o]
    else:
        frontend_origins = [str(origin_setting)]

additional_origins = []
if hasattr(settings, 'ADDITIONAL_ORIGINS') and settings.ADDITIONAL_ORIGINS:
    if isinstance(settings.ADDITIONAL_ORIGINS, list):
        additional_origins = [str(o) for o in settings.ADDITIONAL_ORIGINS if o]
    else:
        additional_origins = [str(settings.ADDITIONAL_ORIGINS)]

# Объединяем все источники и удаляем дубликаты
all_origins = list(set(frontend_origins + telegram_origins + additional_origins))

# В режиме разработки добавляем localhost
if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == "development":
    development_origins = [
        "http://localhost:3000", "http://localhost:5173", "http://localhost:8080",
        "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8080",
    ]
    all_origins.extend(development_origins)
    all_origins = list(set(all_origins)) # Удаляем дубликаты еще раз на всякий случай

cors_logger.info("🌐 CORS configured for origins: %s", all_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID", "X-Process-Time", "X-RateLimit-Limit",
        "X-RateLimit-Remaining", "X-RateLimit-Reset",
    ],
    max_age=86400,
)

# Подключаем API роутер
app.include_router(api_router, prefix="/api")

# Настройка статических файлов
current_file = Path(__file__).resolve()
root_dir = current_file.parents[2]
lib_dir = current_file.parents[1]
dist_candidates = [
    root_dir / "frontend" / "dist",
    lib_dir / "frontend" / "dist",
    root_dir / "dist",
    lib_dir / "dist",
]
dist_dir = next((p for p in dist_candidates if p.is_dir()), None)

if dist_dir:
    logger.info("📦 Front-end mounted from %s", dist_dir)
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets", html=False), name="assets")
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str):
        if request.method == "GET" and not request.url.path.startswith(("/api", "/assets")):
            index_file = dist_dir / "index.html"
            if not index_file.exists():
                logger.error("❌ index.html not found at %s", index_file)
                raise HTTPException(status_code=404, detail="Frontend not available")
            return FileResponse(index_file)
        raise HTTPException(status_code=404)
else:
    logger.warning("❗ dist каталог не найден — фронт не будет отдаваться (искали в %s)", [str(p) for p in dist_candidates])

# Расширенный health check
@app.get("/health", include_in_schema=False)
async def health_check():
    health_status = {
        "status": "ok",
        "timestamp": time.time(),
        "frontend_available": dist_dir is not None,
        "log_level": log_level_name,
        "cors_origins_count": len(all_origins),
    }
    if dist_dir:
        health_status["frontend_path"] = str(dist_dir)
        health_status["index_html_exists"] = (dist_dir / "index.html").exists()
    return health_status

# Endpoint для информации о CORS настройках (только в режиме разработки)
@app.get("/cors-info", include_in_schema=False)
async def cors_info():
    if not (hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == "development"):
        raise HTTPException(status_code=404)
    return {
        "allowed_origins": all_origins,
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        "allow_credentials": True,
        "max_age": 86400,
    }

# События жизненного цикла приложения
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Magic App Backend")
    logger.info("📊 Log level: %s", log_level_name)
    logger.info("🌐 CORS origins: %d configured", len(all_origins))
    logger.info("🔒 Security middleware: enabled")
    logger.info("📁 Frontend available: %s", "Yes" if dist_dir else "No")
    if dist_dir:
        logger.info("📦 Frontend path: %s", dist_dir)
    logger.info("✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Magic App Backend")
    logger.info("✅ Application stopped successfully")
