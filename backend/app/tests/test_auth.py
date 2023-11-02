from app.schemas.user import UserCreate
from app.api.utils.database import get_db
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import User
from app.api.utils.users import get_password_hash,verify_password
from app.api.utils.users import get_user


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    # This will make sure we don't get inconsistencies while writing tests. That's how sqlite works and we have to deal with it
    connect_args={
        "check_same_thread":False,
    },
    # We make sure its a static connection pool so that we connect to the same memory database
    # This will allow us to create something in our database and later read it
    poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def setup():
    SQLModel.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        # Create a user at the beginning of the test
        user_data = UserCreate(email='firstTest@user.com', password=get_password_hash('firstTestPassword'))
        db_user = User(**user_data.model_dump())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

def tearDown():
    SQLModel.metadata.drop_all(bind=engine)

def test_register_user(test_client):
    # Define the user data for registration
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    # Send a POST request to the /register endpoint
    response = test_client.post("/api/v1/auth/register", json=user_data)

    # Assert the response status code and the returned user data
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_verify_created_user():
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstTest@user.com")
    password = get_password_hash("firstTest@user.com")
    assert user.email =="firstTest@user.com"
    assert True == verify_password("firstTest@user.com",password )

def test_login(test_client):
    # Simulate a login request
    user_data = {
        "email": "firstTest@user.com",
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    # Assert the response status code and the returned data
    assert response.status_code == 202 
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_reset_password(test_client):
    # Test case where email is registered
    response = test_client.post("/api/v1/auth/reset-password", json={"email": "firstTest@user.com"})
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset email sent"}

    # Test case where email is not registered
    response = test_client.post("/api/v1/auth/reset-password", json={"email": "nonexistent@example.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Email not registered"}

def test_reset_password_confirm_same_password(test_client):

    user_data = {
        "email": "firstTest@user.com",
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


def test_reset_password_confirm_valid_data(test_client):

    user_data = {
        "email": "firstTest@user.com",
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


def test_reset_password_confirm_bad_token(test_client):

    user_data = {
        "email": "firstTest@user.com",
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
