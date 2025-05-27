"""Add updated_at to categories

Revision ID: 0003
Revises: 0002
Create Date: 2025-05-27 08:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade():
    # Add updated_at column to categories table
    op.add_column(
        'categories',
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    
    # Set updated_at to current time for existing records
    op.execute("""
        UPDATE categories 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE updated_at IS NULL
    """)

def downgrade():
    op.drop_column('categories', 'updated_at')
