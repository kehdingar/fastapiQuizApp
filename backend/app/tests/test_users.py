import pytest
from app.models.user import User, Role
from app.api.utils.database import get_db
from app.main import app
from app.api.utils.users import get_password_hash,verify_password
from app.api.utils.users import get_user
from .conftest import TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_user_with_valid_email(test_client):
    user_data = {
        "email": "valid@email.com",
        "password": "strong_password",
        "role": Role.STUDENT,
    }
    response = test_client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]

def test_create_user_with_invalid_email(test_client):
    user_data = {
        "email": "invalid_email",  # Missing domain
        "password": "strong_password",
        "role": Role.STUDENT,
    }
    response = test_client.post("/api/v1/users", json=user_data)
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()['detail'][0]['msg'] == "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."

def test_create_user_with_duplicate_email(test_client, initial_data):
    email = "firstTest@quiz.com"  # Existing user email
    user_data = {
        "email": email,
        "password": "strong_password",
        "role": Role.STUDENT,
    }
    response = test_client.post("/api/v1/users", json=user_data)
    assert response.status_code == 409  # Conflict
    assert response.json() == {"detail": "email already registered"}

def test_get_all_users(test_client, initial_data,get_instructor_header):
    headers = get_instructor_header
    response = test_client.get("/api/v1/users",headers=headers)
    data = response.json()
    # Adjust based on initial data    
    assert len(data) == 2 

def test_get_user_by_email(test_client, initial_data,get_instructor_header):
    headers = get_instructor_header
    email = "firstTest@quiz.com"
    response = test_client.get(f"/api/v1/users/{email}",headers=headers)
    data = response.json()
    assert data["email"] == email
    assert data["role"] == Role.STUDENT 

def test_delete_user(test_client, initial_data,get_instructor_header):
    headers = get_instructor_header
    email = "firstTest@quiz.com"
    response = test_client.delete(f"/api/v1/users/{email}",headers=headers)
    assert response.status_code == 200

    response = test_client.get("/api/v1/users",headers=headers)
    data = response.json()
    assert len(data) == 1
    assert email not in [user["email"] for user in data]
