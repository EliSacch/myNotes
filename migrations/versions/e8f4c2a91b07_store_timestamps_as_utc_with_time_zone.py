"""store timestamps as utc with time zone

Revision ID: e8f4c2a91b07
Revises: c73a3a5335c6
Create Date: 2026-08-19 18:02:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e8f4c2a91b07"
down_revision = "c73a3a5335c6"
branch_labels = None
depends_on = None

_TABLES = ("Users", "Dashboards", "Notes")
_COLUMNS = ("created_at", "updated_at")


def upgrade():
    for table in _TABLES:
        for column in _COLUMNS:
            op.execute(
                f'ALTER TABLE "{table}" ALTER COLUMN {column} '
                f"TYPE TIMESTAMP WITH TIME ZONE "
                f"USING {column} AT TIME ZONE 'UTC'"
            )


def downgrade():
    for table in _TABLES:
        for column in _COLUMNS:
            op.execute(
                f'ALTER TABLE "{table}" ALTER COLUMN {column} '
                f"TYPE TIMESTAMP WITHOUT TIME ZONE "
                f"USING {column} AT TIME ZONE 'UTC'"
            )
