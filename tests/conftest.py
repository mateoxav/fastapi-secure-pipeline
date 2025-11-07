import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Get the test database URL from the environment variable
# This is set in ci.yml for the CI environment
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://testuser:testpass@localhost:5432/testdb_test")

# Create a new engine and session factory for testing
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Fixture to create and drop the test database tables once per test session.
    """
    # Create all tables before running tests
    Base.metadata.create_all(bind=engine)
    
    yield  # This is where the tests will execute
    
    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture to provide a transactional database session for each test function.
    Rolls back transactions after each test, ensuring a clean state.
    """
    connection = engine.connect()
    # Begin a transaction
    transaction = connection.begin()
    # Bind a session to the transaction
    session = TestingSessionLocal(bind=connection)

    yield session  # This is the session used by the test

    # Roll back the transaction and close the connection
    session.close()
    transaction.rollback()
    connection.close()