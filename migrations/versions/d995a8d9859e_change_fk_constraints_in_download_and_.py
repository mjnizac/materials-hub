"""Change FK constraints in download and view records to materials_dataset

Revision ID: d995a8d9859e
Revises: 003
Create Date: 2025-12-01 09:00:41.273768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'd995a8d9859e'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Drop tables if they exist
    conn = op.get_bind()
    inspector = inspect(conn)

    if 'webhook' in inspector.get_table_names():
        op.drop_table('webhook')
    if 'uvl_dataset' in inspector.get_table_names():
        op.drop_table('uvl_dataset')

    # Get existing foreign key constraints to drop them
    download_fks = inspector.get_foreign_keys('ds_download_record')
    view_fks = inspector.get_foreign_keys('ds_view_record')

    # Drop and recreate foreign keys for ds_download_record
    with op.batch_alter_table('ds_download_record', schema=None) as batch_op:
        for fk in download_fks:
            if fk['constrained_columns'] == ['dataset_id']:
                batch_op.drop_constraint(fk['name'], type_='foreignkey')
        batch_op.create_foreign_key(None, 'materials_dataset', ['dataset_id'], ['id'])

    # Drop and recreate foreign keys for ds_view_record
    with op.batch_alter_table('ds_view_record', schema=None) as batch_op:
        for fk in view_fks:
            if fk['constrained_columns'] == ['dataset_id']:
                batch_op.drop_constraint(fk['name'], type_='foreignkey')
        batch_op.create_foreign_key(None, 'materials_dataset', ['dataset_id'], ['id'])


def downgrade():
    # Get existing foreign key constraints to drop them
    conn = op.get_bind()
    inspector = inspect(conn)
    download_fks = inspector.get_foreign_keys('ds_download_record')
    view_fks = inspector.get_foreign_keys('ds_view_record')

    # Recreate foreign keys pointing to data_set
    with op.batch_alter_table('ds_view_record', schema=None) as batch_op:
        for fk in view_fks:
            if fk['constrained_columns'] == ['dataset_id']:
                batch_op.drop_constraint(fk['name'], type_='foreignkey')
        batch_op.create_foreign_key('ds_view_record_dataset_id_fkey', 'data_set', ['dataset_id'], ['id'])

    with op.batch_alter_table('ds_download_record', schema=None) as batch_op:
        for fk in download_fks:
            if fk['constrained_columns'] == ['dataset_id']:
                batch_op.drop_constraint(fk['name'], type_='foreignkey')
        batch_op.create_foreign_key('ds_download_record_dataset_id_fkey', 'data_set', ['dataset_id'], ['id'])

    # Recreate tables
    op.create_table('uvl_dataset',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('ds_meta_data_id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('webhook',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
