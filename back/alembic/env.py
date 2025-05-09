import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.data.database import base
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.StatsTable import StatsTable
from app.data.models.TagsTable import TagsTable
from app.data.models.EffectsTable import EffectsTable
from app.data.models.MetaDataTable import MetaDataTable
from app.data.models.UserTable import UserTable
from app.data.models.StatsMappingTable import StatsMappingTable
from app.data.models.OrderTable import OrderTable
from app.data.models.CartTable import CartTable
from app.data.models.DeliveryDatesTable import DeliveryDatesTable
from app.data.models.LocationTable import LocationTable
from app.data.models.ReviewTable import ReviewTable

from app.envVariables import DATABASE_ALEMBIC_URL

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_ALEMBIC_URL)
# -------------------------------------------------------------
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel


# Role of the Base Class
# The Base class in SQLAlchemy serves as a registry for all your ORM models.
# When you define a model by inheriting from Base, it gets registered in
# Base.metadata. This metadata is what Alembic uses to understand
# the structure of your database schema. By setting target_metadata = Base.metadata
# in env.py, you're informing Alembic about the schema structure
# it should reference during migrations.


target_metadata = base.metadata
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")

# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
