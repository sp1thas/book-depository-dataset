"""create authors tables

Revision ID: 10df299414ec
Revises: 22fdd5933222
Create Date: 2021-03-15 23:25:02.444473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "10df299414ec"
down_revision = "22fdd5933222"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(126), nullable=False),
    )
    op.create_table(
        "book_author",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("author_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ("book_id",), ["books.id"], name="fk_book_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ("author_id",), ["authors.id"], name="fk_author_id", ondelete="CASCADE"
        ),
    )


def downgrade():
    op.drop_table("book_author")
    op.drop_table("authors")
