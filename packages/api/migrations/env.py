"""Alembic migrations use the same durable model metadata as the API."""

import readout_api.models  # noqa: F401
from alembic import context
from readout_api.repository import database_url, make_engine
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata

if context.is_offline_mode():
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    connectable = make_engine(database_url())
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
