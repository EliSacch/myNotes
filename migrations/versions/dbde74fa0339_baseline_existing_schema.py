"""baseline existing schema

Revision ID: dbde74fa0339
Revises: 
Create Date: 2026-08-09 00:35:54.287881

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'dbde74fa0339'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "Notes",
        sa.Column("NoteId", sa.Integer(), nullable=False),
        sa.Column("IsList", sa.Boolean(), nullable=True),
        sa.Column("Title", sa.String(length=50), nullable=True),
        sa.Column("Content", postgresql.ARRAY(sa.JSON()), nullable=True),
        sa.Column("CreatedAt", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("NoteId"),
    )
    op.create_table(
        "Users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )


def downgrade():
    op.drop_table("Users")
    op.drop_table("Notes")
