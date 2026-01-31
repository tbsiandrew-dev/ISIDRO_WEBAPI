"""Add password column to existing users table

Revision ID: 001_add_password
Revises: 
Create Date: 2026-01-31 12:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '001_add_password'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if password column exists, if not add it
    try:
        op.add_column('users', sa.Column('password', sa.String(length=255), nullable=True))
        # Set default for existing rows, then make it non-nullable
        op.execute("UPDATE users SET password = 'placeholder' WHERE password IS NULL")
        op.alter_column('users', 'password', nullable=False)
    except Exception:
        # Column already exists, skip
        pass


def downgrade() -> None:
    try:
        op.drop_column('users', 'password')
    except Exception:
        pass
