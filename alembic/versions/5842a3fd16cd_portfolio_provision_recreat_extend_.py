"""portfolio provision. recreat / extend FSMStates enum

Revision ID: 5842a3fd16cd
Revises: 6a0fcfdddb38
Create Date: 2019-12-30 11:14:43.985359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5842a3fd16cd' # pragma: allowlist secret
down_revision = '6a0fcfdddb38' # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('portfolio_state_machines', 'state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('portfolio_state_machines', sa.Column('state', sa.VARCHAR(length=27), autoincrement=False, nullable=False))
    # ### end Alembic commands ###