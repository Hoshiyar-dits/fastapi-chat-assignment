from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from app.config.settings import settings
from app.database.base import Base


# Import all models here so Alembic can detect them
from app.conversation.model import Conversation, Message  # noqa: F401  # isort: skip
from app.user.model import User  # noqa: F401  # isort: skip

config = context.config

target_metadata = Base.metadata


def get_sync_database_url() -> str:
    """
    Application uses asyncmy:

        mysql+asyncmy://...

    Alembic uses synchronous PyMySQL:

        mysql+pymysql://...
    """

    url = make_url(settings.database_url)

    sync_url = url.set(
        drivername="mysql+pymysql"
    )

    return sync_url.render_as_string(
        hide_password=False
    )


def run_migrations_offline() -> None:

    url = get_sync_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    configuration = config.get_section(
        config.config_ini_section
    )

    configuration["sqlalchemy.url"] = get_sync_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()