from app.schemas.user import UserCreate
from app.api.auth import get_db
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import User
from app.api.auth import get_password_hash


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
        user_data = UserCreate(email='firstTest@quiz.com', password='firstTestPassword')
        db_user = User(**user_data.model_dump(), hashed_password=get_password_hash(user_data.password))
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