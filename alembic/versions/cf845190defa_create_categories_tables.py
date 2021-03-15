"""create categories tables

Revision ID: cf845190defa
Revises: 10df299414ec
Create Date: 2021-03-15 23:43:54.119232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cf845190defa"
down_revision = "10df299414ec"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(126), nullable=False),
    )
    op.create_table(
        "book_category",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("category_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ("book_id",), ["books.id"], name="fk_book_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ("category_id",),
            ["categories.id"],
            name="fk_category_id",
            ondelete="CASCADE",
        ),
    )


def downgrade():
    op.drop_table("book_category")
    op.drop_table("categories")
