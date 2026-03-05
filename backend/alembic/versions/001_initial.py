"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-03-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "carousels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("slides_count", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_payload", postgresql.JSONB(), nullable=True),
        sa.Column("style_hint", sa.Text(), nullable=True),
        sa.Column("preview_url", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "design_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carousel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template", sa.String(32), nullable=False),
        sa.Column("bg_type", sa.String(16), nullable=False),
        sa.Column("bg_color", sa.String(32), nullable=True),
        sa.Column("bg_image_url", sa.String(1024), nullable=True),
        sa.Column("bg_dim_amount", sa.Float(), nullable=False),
        sa.Column("padding", sa.Integer(), nullable=False),
        sa.Column("align_horizontal", sa.String(16), nullable=False),
        sa.Column("align_vertical", sa.String(16), nullable=False),
        sa.Column("show_header", sa.Boolean(), nullable=False),
        sa.Column("header_text", sa.String(512), nullable=True),
        sa.Column("show_footer", sa.Boolean(), nullable=False),
        sa.Column("footer_text", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("carousel_id"),
    )
    op.create_table(
        "slides",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carousel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("footer", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carousel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(), nullable=True),
        sa.Column("result_payload", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carousel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("zip_url", sa.String(1024), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("carousel_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("assets")
    op.drop_table("exports")
    op.drop_table("generations")
    op.drop_table("slides")
    op.drop_table("design_settings")
    op.drop_table("carousels")
