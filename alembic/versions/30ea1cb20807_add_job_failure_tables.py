"""add job failure tables

Revision ID: 30ea1cb20807
Revises: 0ee5a34a1b84
Create Date: 2019-09-06 06:56:25.685805

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '30ea1cb20807' # pragma: allowlist secret
down_revision = '0ee5a34a1b84' # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('environment_job_failures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(), nullable=False),
    sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('environment_role_job_failures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(), nullable=False),
    sa.Column('environment_role_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['environment_role_id'], ['environment_roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('environment_role_job_failures')
    op.drop_table('environment_job_failures')
    # ### end Alembic commands ###
