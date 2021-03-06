"""add comment info

Revision ID: 38d2c126b4d1
Revises: 17fbf1129656
Create Date: 2019-10-13 14:53:11.120177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38d2c126b4d1'
down_revision = '17fbf1129656'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_received_comment_read_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_received_comment_read_time')
    # ### end Alembic commands ###
