"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Read and execute the initial SQL schema
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'schema', 'initial.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            op.execute(sql)


def downgrade() -> None:
    # Drop custom schema tables if needed
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS processed CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS metadata CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS provenance CASCADE;")
