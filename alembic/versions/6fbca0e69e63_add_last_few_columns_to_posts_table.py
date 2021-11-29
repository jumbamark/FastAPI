"""add last few columns to posts table

Revision ID: 6fbca0e69e63
Revises: cbe3631e6a0d
Create Date: 2021-11-29 10:58:13.615604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fbca0e69e63'
down_revision = 'cbe3631e6a0d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("published", sa.Boolean(),
                  nullable=False, server_default="TRUE"))
    op.add_column("posts", sa.Column("time_posted", sa.TIMESTAMP(
        timezone=True), nullable=False, server_default=sa.text("NOW()")))
    pass


def downgrade():
    op.drop_column("posts", "published")
    op.drop_column("posts", "time_posted")
    pass
