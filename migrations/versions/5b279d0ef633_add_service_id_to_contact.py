"""add service_id to contact

Revision ID: 5b279d0ef633
Revises: d985a1aaeeb8
Create Date: 2026-02-21 11:15:34.337734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b279d0ef633'
down_revision = 'd985a1aaeeb8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_id', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.drop_column('service_id')
