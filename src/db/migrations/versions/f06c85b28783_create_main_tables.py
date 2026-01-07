"""initial model

Revision ID: f06c85b28783
Revises:
Create Date: 2026-01-07 09:25:42.623439

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f06c85b28783"
down_revision = None
branch_labels = None
depends_on = None


def is_deleted() -> sa.Column:
    """Create is_deleted column."""
    return sa.Column(
        "is_deleted", sa.Boolean, nullable=False, server_default=sa.false(), index=True
    )


def timestamps(indexed: bool = False) -> tuple[sa.Column, sa.Column]:
    """Create timestamp in DB."""
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )


def create_images_table() -> None:
    """Create images table."""
    op.create_table(
        "images",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
        ),
        sa.Column(
            "filename",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(50),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "file_size",
            sa.Integer,
            nullable=False,
        ),
        sa.Column(
            "storage_path",
            sa.String(500),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            "content_type IN ('image/jpeg', 'image/png')",
            name="image_content_type_check",
        ),
        *timestamps(),
        is_deleted(),
    )

    op.create_index("idx_images_uploaded_at", "images", ["uploaded_at"])


def create_image_analyses_table() -> None:
    """Create image analyses table."""
    op.create_table(
        "image_analyses",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
        ),
        sa.Column(
            "image_id",
            sa.String(36),
            sa.ForeignKey("images.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "skin_type",
            sa.String(20),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "issues",
            sa.Text,
            nullable=False,
        ),
        sa.Column(
            "confidence_score",
            sa.Float,
            nullable=False,
        ),
        sa.Column(
            "model_version",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "analyzed_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="confidence_score_range_check",
        ),
        sa.CheckConstraint(
            "skin_type IN ('Oily', 'Dry', 'Combination', 'Normal')",
            name="skin_type_check",
        ),
        *timestamps(),
        is_deleted(),
    )

    op.create_index(
        "idx_image_analyses_image_time",
        "image_analyses",
        ["image_id", "analyzed_at"],
    )


def create_api_keys_table() -> None:
    """Create api_keys table."""
    op.create_table(
        "api_keys",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "key_hash",
            sa.String(255),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "scopes",
            sa.Text,
            nullable=False,
        ),  # JSON array: ["upload", "analyze"]
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.true(),
            index=True,
        ),
        *timestamps(indexed=True),
        is_deleted(),
    )

    op.create_index("idx_api_keys_active", "api_keys", ["is_active"])


def upgrade() -> None:
    """Upgrade database"""
    create_images_table()
    create_image_analyses_table()
    create_api_keys_table()


def downgrade() -> None:
    """Downgrade database"""
    tables = [
        "image_analyses",
        "images",
        "api_keys",
    ]

    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
