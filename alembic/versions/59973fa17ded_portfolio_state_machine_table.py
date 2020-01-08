"""portfolio state machine table. 

Revision ID: 59973fa17ded
Revises: 02ac8bdcf16f
Create Date: 2020-01-08 10:37:32.924245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_json

# revision identifiers, used by Alembic.
revision = '59973fa17ded' # pragma: allowlist secret
down_revision = '02ac8bdcf16f' # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('portfolio_job_failures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(), nullable=False),
    sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('portfolio_state_machines',
    sa.Column('time_created', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('time_updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('state', sa.Enum('UNSTARTED', 'STARTING', 'STARTED', 'COMPLETED', 'FAILED', 'TENANT_CREATED', 'TENANT_IN_PROGRESS', 'TENANT_FAILED', 'BILLING_PROFILE_CREATED', 'BILLING_PROFILE_IN_PROGRESS', 'BILLING_PROFILE_FAILED', 'ADMIN_SUBSCRIPTION_CREATED', 'ADMIN_SUBSCRIPTION_IN_PROGRESS', 'ADMIN_SUBSCRIPTION_FAILED', name='fsmstates', native_enum=False), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('portfolios', sa.Column('app_migration', sa.String(), nullable=True))
    op.add_column('portfolios', sa.Column('complexity', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('portfolios', sa.Column('complexity_other', sa.String(), nullable=True))
    op.add_column('portfolios', sa.Column('csp_data', sqlalchemy_json.NestedMutableJson(), nullable=True))
    op.add_column('portfolios', sa.Column('dev_team', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('portfolios', sa.Column('dev_team_other', sa.String(), nullable=True))
    op.add_column('portfolios', sa.Column('native_apps', sa.String(), nullable=True))
    op.add_column('portfolios', sa.Column('team_experience', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('portfolios', 'team_experience')
    op.drop_column('portfolios', 'native_apps')
    op.drop_column('portfolios', 'dev_team_other')
    op.drop_column('portfolios', 'dev_team')
    op.drop_column('portfolios', 'csp_data')
    op.drop_column('portfolios', 'complexity_other')
    op.drop_column('portfolios', 'complexity')
    op.drop_column('portfolios', 'app_migration')
    op.drop_table('portfolio_state_machines')
    op.drop_table('portfolio_job_failures')
    # ### end Alembic commands ###
