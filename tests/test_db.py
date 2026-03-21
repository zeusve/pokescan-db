import os

import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture
def db_connection():
    """Yield a live connection to the PostgreSQL database."""
    if not DATABASE_URL:
        pytest.skip("DATABASE_URL not set — database tests require a running PostgreSQL instance")
    conn = psycopg2.connect(DATABASE_URL)
    yield conn
    conn.close()


def test_connection_succeeds(db_connection):
    """Verify that a connection to PostgreSQL can be established."""
    assert db_connection.closed == 0


def test_pgvector_extension_available(db_connection):
    """Verify that the pgvector extension is loaded."""
    cur = db_connection.cursor()
    cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
    result = cur.fetchone()
    cur.close()
    assert result is not None, "pgvector extension is not installed"
    assert result[0] == "vector"


def test_vector_column_operations(db_connection):
    """Verify that a VECTOR column can be created and queried."""
    cur = db_connection.cursor()
    try:
        cur.execute("CREATE TEMP TABLE _test_vec (id serial PRIMARY KEY, embedding vector(3));")
        cur.execute("INSERT INTO _test_vec (embedding) VALUES ('[1,2,3]');")
        cur.execute("SELECT embedding FROM _test_vec WHERE id = 1;")
        result = cur.fetchone()
        assert result is not None, "Failed to retrieve vector data"
    finally:
        cur.close()
