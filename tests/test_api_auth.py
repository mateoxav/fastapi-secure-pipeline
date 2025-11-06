import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.user import User

# Fixture to create a TestClient
@pytest.fixture
def client():
    return TestClient(app)

# Fixture to get a clean database session for each test
@pytest.fixture
def db_session(mocker):
    # Mock the get_db dependency to use a test session
    # Note: This is a simple mock. For a full test suite, you'd
    # set up a dedicated test database (e.g., via DATABASE_URL env var)
    # and clean it between tests.
    db = mocker.MagicMock(spec=Session)
    
    # Mock app's dependency_overrides to use this mock
    app.dependency_overrides[get_db] = lambda: db
    yield db
    # Clear overrides after test
    app.dependency_overrides = {}


def test_register_user_success(client, db_session):
    # Mock: No user exists
    db_session.query.return_value.filter.return_value.first.return_value = None

    # Test registration
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "a_very_long_password_123"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    
    # Check that user was added and committed
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()


def test_register_user_already_exists(client, db_session):
    # Mock: User *does* exist
    db_session.query.return_value.filter.return_value.first.return_value = User(
        email="test@example.com", hashed_password="abc"
    )

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "a_very_long_password_123"},
    )
    
    # Assert we get the 400 error and the non-specific message
    assert response.status_code == 400
    assert "provided email may already be in use" in response.json()["detail"]


def test_login_success(client, db_session):
    # Mock a valid user in the db
    # Note: We import security functions *within* the test
    # to avoid module-level dependencies
    from app.core.security import hash_password
    valid_pass = "mypassword123"
    hashed_pass = hash_password(valid_pass)
    
    mock_user = User(
        id=1,
        email="login@example.com",
        hashed_password=hashed_pass,
        is_active=True
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Test login
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": valid_pass},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, db_session):
    from app.core.security import hash_password
    hashed_pass = hash_password("mypassword123")
    
    mock_user = User(
        id=1,
        email="login@example.com",
        hashed_password=hashed_pass,
        is_active=True
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Test login with WRONG password
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "wrong_password"},
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_user_not_found(client, db_session):
    # Mock: No user found
    db_session.query.return_value.filter.return_value.first.return_value = None

    response = client.post(
        "/auth/login",
        data={"username": "notauser@example.com", "password": "password"},
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]