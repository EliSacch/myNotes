"""hash user passwords

Revision ID: 3960ffaa10de
Revises: dbde74fa0339
Create Date: 2026-08-09 00:37:59.547009

"""
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = '3960ffaa10de'
down_revision = 'dbde74fa0339'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "Users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )

    connection = op.get_bind()
    users = connection.execute(sa.text('SELECT id, password FROM "Users"')).mappings()
    for user in users:
        connection.execute(
            sa.text(
                'UPDATE "Users" SET password_hash = :password_hash WHERE id = :id'
            ),
            {
                "id": user["id"],
                "password_hash": generate_password_hash(user["password"]),
            },
        )

    op.alter_column("Users", "password_hash", nullable=False)
    op.drop_column("Users", "password")


def downgrade():
    raise RuntimeError("Password hashes cannot be converted back to plaintext passwords.")
