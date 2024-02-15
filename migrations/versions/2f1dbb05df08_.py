"""empty message

Revision ID: 2f1dbb05df08
Revises: 03e389ad5a70
Create Date: 2024-02-12 18:05:00.113614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f1dbb05df08'
down_revision = '03e389ad5a70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_image', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_column('cover_image')

    # ### end Alembic commands ###
