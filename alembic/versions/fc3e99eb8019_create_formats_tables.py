"""create formats tables

Revision ID: fc3e99eb8019
Revises: cf845190defa
Create Date: 2021-03-15 23:46:03.246243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fc3e99eb8019"
down_revision = "cf845190defa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "formats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(126), nullable=False),
    )
    op.create_table(
        "book_format",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("format_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ("book_id",), ["books.id"], name="fk_book_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ("format_id",), ["formats.id"], name="fk_format_id", ondelete="CASCADE"
        ),
    )


def downgrade():
    op.drop_table("book_format")
    op.drop_table("formats")
