"""Add cors_origins table

Revision ID: add_cors_origins_table
Revises: remove_function_trigger_fields
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_cors_origins_table'
down_revision = 'remove_function_trigger_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Check if cors_origins table already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'cors_origins' not in inspector.get_table_names():
        # Create cors_origins table
        op.create_table(
            'cors_origins',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('origin', sa.String(), nullable=False, unique=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
            sa.Column('extra_metadata', postgresql.JSON(), nullable=True, default=dict),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_cors_origins_origin'), 'cors_origins', ['origin'], unique=True)
        op.create_index(op.f('ix_cors_origins_is_active'), 'cors_origins', ['is_active'], unique=False)
    else:
        print("cors_origins table already exists, skipping creation")


def downgrade():
    # Check if cors_origins table exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'cors_origins' in inspector.get_table_names():
        # Drop indexes
        try:
            op.drop_index(op.f('ix_cors_origins_is_active'), table_name='cors_origins')
        except:
            pass
        try:
            op.drop_index(op.f('ix_cors_origins_origin'), table_name='cors_origins')
        except:
            pass
        
        # Drop cors_origins table
        op.drop_table('cors_origins')
    else:
        print("cors_origins table does not exist, skipping drop")