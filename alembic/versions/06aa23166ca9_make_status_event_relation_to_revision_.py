"""make status event relation to revision non-nullable

Revision ID: 06aa23166ca9
Revises: e66a49285f23
Create Date: 2018-09-04 15:03:20.299607

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '06aa23166ca9'
down_revision = 'e66a49285f23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('request_status_events', 'request_revision_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('request_status_events', 'request_revision_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    # ### end Alembic commands ###