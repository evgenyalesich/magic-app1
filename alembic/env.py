# alembic/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Добавляем корень проекта в sys.path, чтобы импортировать backend
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. Импорт моделей
from backend.models import Base  # Убедись, что здесь Base = declarative_base()

# 3. Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

# 4. Настройка Alembic-конфига
config = context.config

# 5. Подменяем URL из .env (asyncpg → psycopg2 для Alembic)
database_url = os.getenv("DATABASE_URL", "")
if "asyncpg" in database_url:
    database_url = database_url.replace("asyncpg", "psycopg2")
config.set_main_option("sqlalchemy.url", database_url)

# 6. Настройка логгера
if config.config_file_name:
    fileConfig(config.config_file_name)

# 7. Метаданные моделей
target_metadata = Base.metadata

# 8. Offline-режим
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 9. Online-режим
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

# 10. Запуск
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
