# ------------------------------------------------------------------------
# magic-app1/alembic/env.py
# ------------------------------------------------------------------------

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context


# ------------------------------------------------------------------------
# 1) Добавляем корень проекта (magic-app1) в sys.path, чтобы
#    можно было импортировать backend.models
# ------------------------------------------------------------------------
current_dir = os.path.dirname(__file__)            # .../magic-app1/alembic
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # .../magic-app1
if project_root not in sys.path:
    sys.path.append(project_root)


# ------------------------------------------------------------------------
# 2) Импортируем SQLAlchemy Base из backend/models.py
#    Именно там у вас должен быть:
#       Base = declarative_base()
#       class User(Base): ...
#       class Product(Base): ...
#       и т. д.
# ------------------------------------------------------------------------
from backend.models import Base  # noqa: E402


# ------------------------------------------------------------------------
# 3) target_metadata нужен, чтобы Alembic знал, с чем сравнивать схему
# ------------------------------------------------------------------------
target_metadata = Base.metadata


# ------------------------------------------------------------------------
# 4) Загружаем конфигурацию Alembic из alembic.ini
# ------------------------------------------------------------------------
config = context.config

# Настройка логгера (настройки берутся из alembic.ini → секции [loggers]/[handlers]/[formatters])
if config.config_file_name:
    fileConfig(config.config_file_name)


# ------------------------------------------------------------------------
# 5) Offline‐режим: генерируем SQL без подключения к БД
# ------------------------------------------------------------------------
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


# ------------------------------------------------------------------------
# 6) Online‐режим: подключаемся к БД и применяем миграции «на лету»
# ------------------------------------------------------------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------------------
# 7) Запускаем нужный блок: offline or online
# ------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
