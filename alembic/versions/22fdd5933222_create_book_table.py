"""create book table

Revision ID: 22fdd5933222
Revises: 
Create Date: 2021-03-15 22:06:18.370495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "22fdd5933222"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "books",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("bestsellers-rank", sa.Integer, nullable=True),
        sa.Column("description", sa.Unicode(1024), nullable=True),
        sa.Column("dimension-x", sa.Float, nullable=True),
        sa.Column("dimension-y", sa.Float, nullable=True),
        sa.Column("dimension-z", sa.Float, nullable=True),
        sa.Column("edition", sa.Unicode, nullable=True),
        sa.Column("edition-statement", sa.Unicode, nullable=True),
        sa.Column("for-ages", sa.Unicode, nullable=True),
        sa.Column("illustrations-note", sa.Unicode, nullable=True),
        sa.Column("image-checksum", sa.String(32), nullable=True),
        sa.Column("image-path", sa.Unicode(1024), nullable=True),
        sa.Column("image-url", sa.Unicode(1024), nullable=True),
        sa.Column("imprint", sa.Unicode(1024), nullable=True),
        sa.Column("index-date", sa.Date, nullable=True),
        sa.Column("isbn10", sa.Unicode(24), nullable=True),
        sa.Column("isbn13", sa.Unicode(24), nullable=True),
        sa.Column("lang", sa.Unicode(12), nullable=True),
        sa.Column("publication-date", sa.DateTime, nullable=True),
        sa.Column("publication-place", sa.Unicode, nullable=True),
        sa.Column("rating-avg", sa.Float, nullable=True),
        sa.Column("rating-count", sa.Integer, nullable=True),
        sa.Column("title", sa.Unicode(1024), nullable=True),
        sa.Column("url", sa.Unicode(1024), nullable=True),
        sa.Column("weight", sa.Float, nullable=True),
    )


def downgrade():
    op.drop_table("books")
