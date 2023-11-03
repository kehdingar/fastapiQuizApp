from app.schemas.user import UserCreate
from app.schemas.category import CategoryCreate
from app.models.category import Category
from app.api.utils.database import get_db
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import Role, User
from app.api.auth import get_password_hash



SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    # This will make sure we don't get inconsistencies while writing tests. Tha's how sqlite works and we have to deal with it
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
    with TestingSessionLocal() as session:
        # Create necessary tables for each test case
        SQLModel.metadata.create_all(bind=session.get_bind())

        # Create Instructor user at the beninning of the test

        instructor_data = {
            "email":'firstInstructorTest@quiz.com', 
            "password":get_password_hash('firstInsructorTestPassword'),
            "role" :Role.INSTRUCTOR,
            }
        instructor_db_user = User(email=instructor_data['email'],password=instructor_data['password'],role=instructor_data['role'])

        # Create a user at the beginning of the test
        user_data = UserCreate(email='firstTest@quiz.com', password=get_password_hash('firstTestPassword'))
        db_user = User(**user_data.model_dump())
        session.add(db_user)
        session.add(instructor_db_user)
        session.commit()
        session.refresh(db_user)
        session.refresh(instructor_db_user)

        category_data = CategoryCreate(name="BACKEND")
        db_category = Category(**category_data.model_dump())

        category_data_2 = CategoryCreate(name="FRONTEND")
        db_category_2 = Category(**category_data_2.model_dump())

        session.add(db_category)
        session.add(db_category_2)
        session.commit()
        session.refresh(db_category)
        session.refresh(db_category_2)

def tearDown():
    SQLModel.metadata.drop_all(bind=engine)

def test_fetch_all_categories(test_client):

    # Send a request to create a question with the authenticated token
    response = test_client.get("/api/v1/categories/")
    # Assert the response status code
    assert response.status_code == 200
    # Check if 'BACKEND' is present in the 'name' field of each dictionary
    assert len(response.json()) == 2 # Check the length of the list

def test_fetch_all_categories_by_id(test_client):

    # Send a request to create a question with the authenticated token
    response = test_client.get("/api/v1/categories/2")
    # Assert the response status code
    assert response.status_code == 200
