"""Add text style fields to design_settings

Revision ID: 002
Revises: 001
Create Date: 2026-03-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.add_column(
      "design_settings",
      sa.Column("title_font_size", sa.Integer(), nullable=False, server_default="32"),
  )
  op.add_column(
      "design_settings",
      sa.Column("body_font_size", sa.Integer(), nullable=False, server_default="18"),
  )
  op.add_column(
      "design_settings",
      sa.Column("highlight_color", sa.String(length=32), nullable=True),
  )
  # Убираем server_default, чтобы дальнейшие вставки шли через приложение
  op.alter_column("design_settings", "title_font_size", server_default=None)
  op.alter_column("design_settings", "body_font_size", server_default=None)


def downgrade() -> None:
  op.drop_column("design_settings", "highlight_color")
  op.drop_column("design_settings", "body_font_size")
  op.drop_column("design_settings", "title_font_size")

