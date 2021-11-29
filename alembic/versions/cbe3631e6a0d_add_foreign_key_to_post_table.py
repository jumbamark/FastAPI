"""add foreign key to post table

Revision ID: cbe3631e6a0d
Revises: 9647d9aa73cd
Create Date: 2021-11-29 10:29:09.908080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbe3631e6a0d'
down_revision = '9647d9aa73cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("owner_id", sa.Integer(), nullable=False))
    # set the link between the two tables
    op.create_foreign_key("posts_users_fk", source_table="posts", referent_table="users", local_cols=[
        "owner_id"], remote_cols=["id"], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint("posts_users_fk", table_name="posts")
    op.drop_column("posts", "owner_id")
    pass
