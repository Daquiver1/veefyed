"""This module is used to run the migrations in the database."""

import pathlib
import sys
from logging.config import fileConfig

import alembic
from sqlalchemy import engine_from_config, pool

# appending the app directory to path so we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

# Third party imports
from src.core.config import DATABASE_URL
from src.utils.formatters import Formatters

# Alembic config object, which provide access to values within the .ini file
config = alembic.context.config

# Interpret the config file for logging
fileConfig(config.config_file_name)  # type: ignore

MODIFIED_DATABASE_URL = Formatters.modify_database_url(str(DATABASE_URL))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    alembic.context.configure(url=MODIFIED_DATABASE_URL)

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    DB_URL = str(MODIFIED_DATABASE_URL)

    connectable = config.attributes.get("connection")
    config.set_main_option("sqlalchemy.url", DB_URL)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    with connectable.connect() as connection:
        alembic.context.configure(connection=connection, target_metadata=None)
        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
