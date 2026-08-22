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
    """Load the initial schema.

    IMPORTANT: this file has multiple CREATE TABLE/TRIGGER/FUNCTION statements,
    including a dollar-quoted ($$...$$) function body with embedded semicolons.
    A single op.execute(sql) call with the whole file was found to silently
    execute only a partial subset (or nothing) depending on driver/DBAPI
    behavior, with NO error raised — a dangerous silent failure. To guarantee
    correctness, we run the file the same way it was manually verified to
    work: as one raw multi-statement script sent directly to the DBAPI
    connection in autocommit mode (mirrors what `psql -f` does).
    """
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'schema', 'initial.sql')
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Required schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    if not sql.strip():
        raise ValueError(f"Schema file is empty: {schema_path}")

    connection = op.get_bind()
    raw_connection = connection.connection
    previous_autocommit = raw_connection.autocommit
    raw_connection.autocommit = True
    try:
        cursor = raw_connection.cursor()
        cursor.execute(sql)
        cursor.close()
    finally:
        raw_connection.autocommit = previous_autocommit


def downgrade() -> None:
    # Drop custom schema tables if needed
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS processed CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS metadata CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS provenance CASCADE;")