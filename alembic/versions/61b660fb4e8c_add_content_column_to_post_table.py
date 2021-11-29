"""add content column to post table

Revision ID: 61b660fb4e8c
Revises: fa80de2a2383
Create Date: 2021-11-28 22:46:17.706946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61b660fb4e8c'
down_revision = 'fa80de2a2383'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "posts",
        sa.Column("content", sa.String(), nullable=False)
    )
    pass


def downgrade():
    op.drop_column("posts", "content")
    pass
