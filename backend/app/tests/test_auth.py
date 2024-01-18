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

def test_initial_test_user(initial_data):
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    assert user.email =="firstTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Student"


def test_initial_test_instructor_user(initial_data):
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstInstructorTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    assert user.email =="firstInstructorTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Instructor"

def test_register_user(test_client,initial_data, get_instructor_header):
    headers = get_instructor_header
    # Define the user data for registration
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    # Send a POST request to the /register endpoint
    response = test_client.post("/api/v1/auth/register", json=user_data, headers=headers)

    # Assert the response status code and the returned user data
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_verify_created_user(initial_data):
    db = TestingSessionLocal()
    regular_user = initial_data["regular_user"]
    user = get_user(db=db, email=regular_user.email)
    password = get_password_hash(regular_user.email)
    assert user.email == regular_user.email
    assert True == verify_password(regular_user.email,password )

def test_login(test_client,initial_data):
    # Simulate a login request
    regular_user = initial_data["regular_user"]

    user_data = {
        "email": regular_user.email,
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    # Assert the response status code and the returned data
    assert response.status_code == 202 
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_reset_password(test_client,initial_data):

    regular_user = initial_data["regular_user"]
    # Test case where email is registered
    response = test_client.post("/api/v1/auth/reset-password", json={"email":regular_user.email})
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset email sent"}

    # Test case where email is not registered
    response = test_client.post("/api/v1/auth/reset-password", json={"email": "nonexistent@example.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Email not registered"}

def test_reset_password_confirm_same_password(test_client,initial_data):
    regular_user = initial_data["regular_user"]

    user_data = {
        "email": regular_user.email,
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()

    # Access the access_token
    token = content_dict["access_token"]

    user_reset_data_same = {
        "token": token,
        "password": "firstTestPassword"
    }
    # # Test case where old and new passwords are the same
    response = test_client.post("/api/v1/auth/reset-password-confirm", json=user_reset_data_same)
    # old_password = get_user(email=user_data['email'],db = session).password
    # new_password = user_reset_data_same["password"]
    # assert old_password == new_password
    assert response.status_code == 226
    assert response.json() == {"detail": "New password is the same as the old password. Please choose a different password"}


def test_reset_password_confirm_valid_data(test_client,initial_data):
    regular_user = initial_data["regular_user"]

    user_data = {
        "email": regular_user.email,
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()

    # Access the access_token
    token = content_dict["access_token"]

    user_reset_data = {
        "token": token,
        "password": "firstTestPassword2"
    }

    # Test case where token is valid and email is registered
    response = test_client.post("/api/v1/auth/reset-password-confirm", json=user_reset_data)
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset successful"}


def test_reset_password_confirm_bad_token(test_client,initial_data):
    regular_user = initial_data["regular_user"]

    user_data = {
        "email": regular_user.email,
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)


    user_reset_data_bad_token = {
        "token": "bad_token",
        "password": "firstTestPassword2"
    }

    # Test case where token is invalid
    response = test_client.post("/api/v1/auth/reset-password-confirm", json=user_reset_data_bad_token)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token"}
