import os, time, sys
import psycopg  # PostgreSQL client library
from alembic.config import Config  # Alembic configuration loader
from alembic import command  # Alembic migration commands

# Get the database URL from environment variables
DB_URL = os.environ.get("DATABASE_URL")

# Exit if is not configured
if not DB_URL:
    print("Error: DATABASE_URL environment variable is not set.", file=sys.stderr)
    sys.exit("DATABASE_URL not set")

# psycopg (used for wait_db and the lock) requires a ‘postgresql://’ URL
# SQLAlchemy (used by Alembic) requires ‘postgresql+psycopg://’
# We create a version of the URL specific to psycopg
PSYCOPG_DB_URL = DB_URL.replace("postgresql+psycopg://", "postgresql://")

# Arbitrary constant used for advisory locking
LOCK_KEY = 42

# Function to wait until the database is ready
def wait_db(url: str, attempts=60, sleep=2):
    for i in range(attempts):
        try:
            # Try to connect to the database with a short timeout
            with psycopg.connect(url, connect_timeout=3) as _:
                print("[wait_db] DB connection successful.")
                return True  # Connection successful
        except Exception as e:
            # Añadido: Imprime el error para depuración
            print(f"[wait_db] DB not ready (Attempt {i+1}/{attempts}). Retrying... Error: {e}", file=sys.stderr)
            time.sleep(sleep)  # Wait before retrying
    return False  # Failed to connect after all attempts


# Exit if the database URL is missing or the DB is not ready
if not wait_db(PSYCOPG_DB_URL): 
    sys.exit("DB not ready after multiple attempts.")

# Connect to the database with autocommit enabled
with psycopg.connect(PSYCOPG_DB_URL, autocommit=True) as conn: 
    with conn.cursor() as cur:
        # Try to acquire an advisory lock to prevent concurrent migrations
        print("[migrate.py] Waiting to acquire migration lock...")
        while True:
            cur.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_KEY,))
            if cur.fetchone()[0]:  # Lock acquired
                print("[migrate.py] Migration lock acquired.")
                break
            time.sleep(1)  # Wait and retry

        try:
            # Load Alembic configuration and apply migrations up to the latest version
            print("[migrate.py] Running Alembic migrations (upgrade head)...")
            cfg = Config("alembic.ini")
            # Alembic usará la variable de entorno DATABASE_URL original 
            # (leída desde alembic/env.py), lo cual es correcto.
            command.upgrade(cfg, "head")
            print("[migrate.py] Migrations applied successfully.")
        finally:
            # Release the advisory lock
            cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
            print("[migrate.py] Migration lock released.")