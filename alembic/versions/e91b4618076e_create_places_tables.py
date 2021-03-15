"""create places tables

Revision ID: e91b4618076e
Revises: fc3e99eb8019
Create Date: 2021-03-15 23:46:08.352368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e91b4618076e"
down_revision = "fc3e99eb8019"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "places",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(126), nullable=False),
    )
    op.create_table(
        "book_place",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("place_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(("book_id",), ["places.id"], name="fk_book_id"),
        sa.ForeignKeyConstraint(("place_id",), ["places.id"], name="fk_place_id"),
    )


def downgrade():
    op.drop_table("book_place")
    op.drop_table("places")
