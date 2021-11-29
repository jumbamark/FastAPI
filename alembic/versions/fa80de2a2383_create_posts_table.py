"""create posts table

Revision ID: fa80de2a2383
Revises: 
Create Date: 2021-11-28 15:21:29.590635

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fa80de2a2383"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        # columns
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
    )

    pass


def downgrade():
    op.drop_table("posts")
    pass
