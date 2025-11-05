import os, time, sys
import psycopg  # PostgreSQL client library
from alembic.config import Config  # Alembic configuration loader
from alembic import command  # Alembic migration commands

# Get the database URL from environment variables
DB_URL = os.environ.get("DATABASE_URL")

# Arbitrary constant used for advisory locking
LOCK_KEY = 42

# Function to wait until the database is ready
def wait_db(url: str, attempts=60, sleep=2):
    for _ in range(attempts):
        try:
            # Try to connect to the database with a short timeout
            with psycopg.connect(url, connect_timeout=3) as _:
                return True  # Connection successful
        except Exception:
            time.sleep(sleep)  # Wait before retrying
    return False  # Failed to connect after all attempts

# Exit if the database URL is missing or the DB is not ready
if not DB_URL or not wait_db(DB_URL):
    sys.exit("DB not ready")

# Connect to the database with autocommit enabled
with psycopg.connect(DB_URL, autocommit=True) as conn:
    with conn.cursor() as cur:
        # Try to acquire an advisory lock to prevent concurrent migrations
        while True:
            cur.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_KEY,))
            if cur.fetchone()[0]:  # Lock acquired
                break
            time.sleep(1)  # Wait and retry

        try:
            # Load Alembic configuration and apply migrations up to the latest version
            cfg = Config("alembic.ini")
            command.upgrade(cfg, "head")
        finally:
            # Release the advisory lock
            cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
