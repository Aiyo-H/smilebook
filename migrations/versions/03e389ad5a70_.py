"""empty message

Revision ID: 03e389ad5a70
Revises: 32c24b7d97c9
Create Date: 2024-01-31 15:36:12.569794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03e389ad5a70'
down_revision = '32c24b7d97c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_image', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('avatar_image')

    # ### end Alembic commands ###
