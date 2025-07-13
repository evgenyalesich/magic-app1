from cx_Freeze import setup, Executable
import os

build_exe_options = {
    "packages": [
        "aiofiles",
        "aiogram",
        "aiohttp",
        "alembic",
        "asyncpg",
        "email_validator",
        "fastapi",
        "httpx",
        "sqlalchemy",
        "starlette",
        "uvicorn",
        "pydantic",
        "pydantic_settings",
        "dotenv",
        "psycopg2",
        "yarl",
        "websockets",
        "httptools",
        "itsdangerous",
        "telegram_webapp_auth",
    ],
    "include_files": [
        # Удалили принудительное включение openssl_stable_libs
        # cx_Freeze теперь должен находить системные OpenSSL
        ("backend", "backend"),
        ("bot", "bot"),
        ("alembic", "alembic"),
        (".env", ".env"),
        ("frontend/dist", "lib/frontend/dist"),
    ],
    "excludes": [
        "pytest",
        "__pycache__",
        ".pytest_cache",
    ],

    # Удалили 'bin_excludes' для OpenSSL
    "build_exe": "magic_app",
}

# Для Linux-окружения base=None (консольное приложение)
base = None

executables = [
    Executable(
        script="run.py",
        base=base,
        target_name="magic_app",
    )
]

setup(
    name="MagicApp",
    version="1.0",
    description="Зеркало Судьбы Telegram bot & WebApp",
    options={"build_exe": build_exe_options},
    executables=executables,
)
