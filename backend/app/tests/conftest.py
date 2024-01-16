import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.main import app
from app.api.utils.users import get_password_hash
from app.models.user import Role, User
from app.schemas.user import UserCreate
from app.models.category import Category
from app.schemas.category import CategoryCreate


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @pytest.fixture(scope="session")
@pytest.fixture(autouse=True)
def database_setup():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture
def initial_data(database_setup):
    with TestingSessionLocal() as session:
        # Create Instructor user at the beginning of the test
        instructor_data = {
            "email": 'firstInstructorTest@quiz.com',
            "password": get_password_hash('firstInstructorTestPassword'),
            "role": Role.INSTRUCTOR,
        }
        instructor_db_user = User(
            email=instructor_data['email'],
            password=instructor_data['password'],
            role=instructor_data['role']
        )

        # Create a user at the beginning of the test
        user_data = UserCreate(
            email='firstTest@quiz.com',
            password=get_password_hash('firstTestPassword')
        )        
        db_user = User(**user_data.model_dump())
        session.add(db_user)
        session.add(instructor_db_user)

        category_data = CategoryCreate(name="BACKEND")
        db_category = Category(**category_data.model_dump())
        session.add(db_category)

        category_data_2 = CategoryCreate(name="FRONTEND")
        db_category_2 = Category(**category_data_2.model_dump())
        session.add(db_category_2)
        session.commit()

        session.refresh(db_user)
        session.refresh(instructor_db_user)
        session.refresh(db_category)
        session.refresh(db_category_2)

        return {
            "instructor_user": instructor_db_user,
            "regular_user": db_user,
            "category_1": db_category,
            "category_2": db_category_2,
        }

@pytest.fixture
def get_instructor_header(test_client,initial_data):
    instructor_user = initial_data['instructor_user']
    user_data = {
        "email": instructor_user.email,
        "password": "firstInstructorTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()
    # Access the access_token
    token = content_dict["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

@pytest.fixture
def get_student_header(test_client,initial_data):
    regular_user = initial_data['regular_user']
    user_data = {
        "email": regular_user.email,
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()

    # Access the access_token
    token = content_dict["access_token"]       
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers
