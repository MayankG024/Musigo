from __future__ import annotations

from logging.config import fileConfig
import os
import sys
from sqlalchemy import pool
from alembic import context
from sqlalchemy import engine_from_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Ensure backend root is on sys.path so 'api' and 'models' are importable
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if backend_root not in sys.path:
    sys.path.append(backend_root)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# import models' metadata
from api.core.database import Base
import models.user  # noqa
import models.music  # noqa
import models.playlist  # noqa

target_metadata = Base.metadata

def _normalize_sync_url(url: str) -> str:
    """Convert async driver URLs to sync equivalents for Alembic engine.

    - postgresql+asyncpg -> postgresql+psycopg2
    - sqlite+aiosqlite   -> sqlite
    """
    if not url:
        return url
    if url.startswith("postgresql+asyncpg"):
        return url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    if url.startswith("sqlite+aiosqlite"):
        return url.replace("sqlite+aiosqlite", "sqlite", 1)
    return url

# Set SQLAlchemy URL from env if present, normalizing to sync driver
db_url = os.getenv("DATABASE_URL")
if db_url:
    sync_url = _normalize_sync_url(db_url)
    config.set_section_option("alembic", "sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
