"""Initial experiment registry and independently durable analysis records."""

import readout_api.models  # noqa: F401
from alembic import op
from sqlmodel import SQLModel

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    SQLModel.metadata.create_all(op.get_bind())


def downgrade() -> None:
    SQLModel.metadata.drop_all(op.get_bind())
