import sys
from pathlib import Path

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Make "backend" importable when alembic is run from the project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import settings
from backend.database import Base
# Import every model so it's registered on Base.metadata before autogenerate runs
from backend.models import user, account, category, transaction, budget  # noqa: F401
from backend.models import investment  # noqa: F401  (Milestone 2, Part 1)
from backend.models import price_cache  # noqa: F401  (Milestone 2, Part 2)
from backend.models import goal  # noqa: F401  (Milestone 2, Part 3)
from backend.models import trade  # noqa: F401  (Milestone 2, Trading extension)
from backend.models import notification, user_session  # noqa: F401 (Milestone 3)
from backend.models import financial_health  # noqa: F401 (Financial Health Module)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Use the same DATABASE_URL the app itself uses, instead of a separate value
# hardcoded in alembic.ini - keeps migrations pointed at the real DB.

# TEMPORARY DIAGNOSTIC - remove once the Render env var issue is confirmed
# and fixed. Prints where DATABASE_URL is actually resolving to (with the
# password masked) and whether an unexpected .env file is present, so we
# can tell definitively whether the env var is reaching this process.
import os
_masked = settings.DATABASE_URL
if "@" in _masked:
    _scheme_and_user, _rest = _masked.split("@", 1)
    if ":" in _scheme_and_user.split("//", 1)[-1]:
        _scheme, _cred = _scheme_and_user.split("//", 1)
        _user = _cred.split(":", 1)[0]
        _masked = f"{_scheme}//{_user}:***@{_rest}"
print(f"[DIAGNOSTIC] settings.DATABASE_URL resolves to: {_masked}", flush=True)
print(f"[DIAGNOSTIC] os.environ has DATABASE_URL set: {'DATABASE_URL' in os.environ}", flush=True)
print(f"[DIAGNOSTIC] cwd: {os.getcwd()}", flush=True)
print(f"[DIAGNOSTIC] .env exists in cwd: {os.path.exists('.env')}", flush=True)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
