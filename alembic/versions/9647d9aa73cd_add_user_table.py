"""add user table

Revision ID: 9647d9aa73cd
Revises: 61b660fb4e8c
Create Date: 2021-11-28 23:31:50.240270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9647d9aa73cd'
down_revision = '61b660fb4e8c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("email", sa.String(), nullable=False),
                    sa.Column("password", sa.String(), nullable=False),
                    sa.Column("time_created", sa.TIMESTAMP(timezone=True),
                              server_default=sa.text("now()"), nullable=False),
                    sa.PrimaryKeyConstraint("id"),
                    sa.UniqueConstraint("email")
                    )
    pass


def downgrade():
    op.drop_table("users")
    pass
