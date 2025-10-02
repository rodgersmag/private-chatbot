"""Change file size column from Integer to BigInteger

Revision ID: change_file_size_to_biginteger
Revises: remove_function_trigger_fields
Create Date: 2025-06-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'change_file_size_to_biginteger'
down_revision = 'remove_function_trigger_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Change size column from Integer to BigInteger to support files larger than 2GB"""
    # Change size column from Integer to BigInteger
    op.alter_column('files', 'size',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)


def downgrade():
    """Change size column back to Integer"""
    # Note: This downgrade could cause data loss if there are files larger than 2GB
    # Change size column back to Integer
    op.alter_column('files', 'size',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
