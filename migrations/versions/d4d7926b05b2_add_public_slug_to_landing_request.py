"""add public_slug to landing_request

Revision ID: d4d7926b05b2
Revises: f60373e35def
Create Date: 2026-02-18 12:01:35.085632

"""
import secrets
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4d7926b05b2'
down_revision = 'f60373e35def'
branch_labels = None
depends_on = None


def upgrade():
    # Add column as nullable first
    with op.batch_alter_table('landing_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('public_slug', sa.String(length=16), nullable=True))

    # Backfill existing rows with unique slugs
    conn = op.get_bind()
    rows = conn.execute(sa.text('SELECT id FROM landing_request WHERE public_slug IS NULL')).fetchall()
    for row in rows:
        slug = secrets.token_urlsafe(8)
        conn.execute(sa.text('UPDATE landing_request SET public_slug = :slug WHERE id = :id'), {'slug': slug, 'id': row[0]})

    # Now set NOT NULL and unique constraint
    with op.batch_alter_table('landing_request', schema=None) as batch_op:
        batch_op.alter_column('public_slug', nullable=False)
        batch_op.create_unique_constraint('uq_landing_request_public_slug', ['public_slug'])


def downgrade():
    with op.batch_alter_table('landing_request', schema=None) as batch_op:
        batch_op.drop_constraint('uq_landing_request_public_slug', type_='unique')
        batch_op.drop_column('public_slug')
