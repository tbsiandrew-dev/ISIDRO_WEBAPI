"""Alembic environment configuration for async SQLAlchemy"""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Import models
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web.database import Base

# Dynamically import all models from __all__ to register them with Base.metadata
from web import models
for model_name in models.__all__:
    globals()[model_name] = getattr(models, model_name)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Build database URL from environment
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace('+asyncpg', ''))
    context.configure(
        url=DATABASE_URL.replace('+asyncpg', ''),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
