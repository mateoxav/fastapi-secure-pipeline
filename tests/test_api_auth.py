import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

# Note: The 'client' and 'db_session' fixtures are automatically provided
# from tests/conftest.py. We just need to type-hint them.

def test_register_user_success(client: TestClient, db_session: Session):
    # No mocks needed. We just make the request.
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "a_very_long_password_123"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    
    # Verify the user was actually created in the database
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"


def test_register_user_already_exists(client: TestClient, db_session: Session):
    # Setup: Create the user in the DB first
    existing_user = User(
        email="test@example.com", 
        hashed_password=hash_password("password123")
    )
    db_session.add(existing_user)
    db_session.commit()

    # Test: Try to register the same user again
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "a_very_long_password_123"},
    )
    
    # Assert we get the 400 error
    assert response.status_code == 400
    assert "provided email may already be in use" in response.json()["detail"]


def test_login_success(client: TestClient, db_session: Session):
    # Setup: Create a valid user
    valid_pass = "mypassword123"
    hashed_pass = hash_password(valid_pass)
    mock_user = User(
        id=1,
        email="login@example.com",
        hashed_password=hashed_pass,
        is_active=True
    )
    db_session.add(mock_user)
    db_session.commit()

    # Test login
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": valid_pass},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, db_session: Session):
    # Setup: Create a valid user
    hashed_pass = hash_password("mypassword123")
    mock_user = User(
        id=1,
        email="login@example.com",
        hashed_password=hashed_pass,
        is_active=True
    )
    db_session.add(mock_user)
    db_session.commit()

    # Test login with WRONG password
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "wrong_password"},
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_user_not_found(client: TestClient):
    # No setup needed, the DB is empty (due to rollback)
    response = client.post(
        "/auth/login",
        data={"username": "notauser", "password": "irrelevant"},
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]