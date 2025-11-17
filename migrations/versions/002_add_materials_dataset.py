"""add materials dataset and material record models

Revision ID: 002
Revises: 001
Create Date: 2025-01-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create materials_dataset table
    op.create_table(
        'materials_dataset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ds_meta_data_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('csv_file_path', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create material_record table
    op.create_table(
        'material_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('materials_dataset_id', sa.Integer(), nullable=False),
        sa.Column('material_name', sa.String(length=256), nullable=False),
        sa.Column('chemical_formula', sa.String(length=256), nullable=True),
        sa.Column('structure_type', sa.String(length=256), nullable=True),
        sa.Column('composition_method', sa.String(length=256), nullable=True),
        sa.Column('property_name', sa.String(length=256), nullable=False),
        sa.Column('property_value', sa.String(length=256), nullable=False),
        sa.Column('property_unit', sa.String(length=128), nullable=True),
        sa.Column('temperature', sa.Integer(), nullable=True),
        sa.Column('pressure', sa.Integer(), nullable=True),
        sa.Column('data_source', sa.Enum('EXPERIMENTAL', 'COMPUTATIONAL', 'LITERATURE', 'DATABASE', 'OTHER', name='datasource'), nullable=True),
        sa.Column('uncertainty', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['materials_dataset_id'], ['materials_dataset.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create uvl_dataset table (migrating from data_set)
    # Note: We keep data_set table for backward compatibility
    op.create_table(
        'uvl_dataset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ds_meta_data_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('material_record')
    op.drop_table('materials_dataset')
    op.drop_table('uvl_dataset')

    # Drop enum type (PostgreSQL specific, won't affect SQLite)
    op.execute('DROP TYPE IF EXISTS datasource')
