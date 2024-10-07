"""Added users table

Revision ID: 25b556f883b8
Revises:
Create Date: 2024-08-22 04:19:34.619552

"""

from os import walk
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "25b556f883b8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("created", sa.DateTime(timezone=True)),
        sa.Column("name", sa.String(length=30), unique=False, index=True),
        sa.Column("password", sa.String(length=254), nullable=False, index=True),
        sa.Column("salt", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, index=True),
        sa.Column("uuid", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column(
            "signed_up_method", sa.String(length=254), nullable=False, default="email"
        ),
    )

    # Create albums table
    op.create_table(
        "albums",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=30), unique=False, index=True),
        sa.Column("album_name", sa.String(length=254), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=True, default=True),
    )

    # Create photos table
    op.create_table(
        "photos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "album_id",
            sa.Integer(),
            sa.ForeignKey("albums.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.DateTime(timezone=True)),
        sa.Column("file_name", sa.String(length=254), nullable=False),
    )

    # Create networks table
    op.create_table(
        "networks",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "founder_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "album_id",
            sa.Integer,
            sa.ForeignKey("albums.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("networks")
    op.drop_table("photos")
    op.drop_table("albums")
    op.drop_table("users")
