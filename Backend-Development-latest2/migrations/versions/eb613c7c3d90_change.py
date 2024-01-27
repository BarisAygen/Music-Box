"""change

Revision ID: eb613c7c3d90
Revises: f3d08b28ee7e
Create Date: 2024-01-18 19:46:02.075364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb613c7c3d90'
down_revision = 'f3d08b28ee7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('googleID', sa.String(length=150), nullable=True))
        batch_op.create_unique_constraint(None, ['googleID'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('googleID')

    # ### end Alembic commands ###