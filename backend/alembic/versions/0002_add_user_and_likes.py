"""Add user and likes tables

Revision ID: 0002
Revises: 0001
Create Date: 2025-05-26 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False)
    )
    
    # Add like_count to prompts table
    op.add_column('prompts', sa.Column('like_count', sa.Integer(), server_default='0', nullable=False))
    
    # Create user_likes table
    op.create_table(
        'user_likes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('user_id', 'prompt_id', name='uq_user_like')
    )
    
    # Create index for faster lookups
    op.create_index('idx_user_likes_user', 'user_likes', ['user_id'])
    op.create_index('idx_user_likes_prompt', 'user_likes', ['prompt_id'])

def downgrade():
    op.drop_index('idx_user_likes_prompt', table_name='user_likes')
    op.drop_index('idx_user_likes_user', table_name='user_likes')
    op.drop_table('user_likes')
    op.drop_column('prompts', 'like_count')
    op.drop_table('users')
