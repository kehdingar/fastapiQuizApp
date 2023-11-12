import pytest
from app.schemas.user import UserCreate
from app.api.auth import get_db, get_user
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import Role, User
from app.api.auth import get_password_hash
from app.api.auth import verify_password
from app.schemas.category import CategoryCreate




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


def test_initial_test_user():
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    assert user.email =="firstTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Student"


def test_initial_test_instructor_user():
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstInstructorTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    print(f"\n user role {user.role}")
    assert user.email =="firstInstructorTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Instructor"

def test_create_questions_no_previledge(test_client):

    user_data = {
        "email": "firstTest@quiz.com",
        "password": "firstTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()

    # Access the access_token
    token = content_dict["access_token"]

    # Multiple Payload items
    question_payload = [
        {
            "question": {
                "text": "What is the capital of Cameroon?",
                "category_id": 1
            },
            "options": [
                {
                    "answer": "Yaounde",
                    "is_correct": True
                },
                {
                    "answer": "Douala",
                    "is_correct": False
                },
                {
                    "answer": "USA",
                    "is_correct": False
                }
            ]
        },
        {
            "question": {
                "text": "What is the capital of America?",
                "category_id": 2
            },
            "options": [
                {
                    "answer": "Washington DC",
                    "is_correct": True
                },
                {
                    "answer": "Kiev",
                    "is_correct": False
                },
                {
                    "answer": "Atlanta",
                    "is_correct": False
                }
            ]
        }
    ]    


    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send a request to create a question with the authenticated token
    response = test_client.post("/api/v1/questions/", json=question_payload, headers=headers)
    print(f"\n\n RESO {response.json()}")
    # Assert the response status code
    assert response.status_code == 403
    # Assert the response body
    assert response.json() == {'detail': 'Insufficient privileges'}


@pytest.fixture
def create_questions_previldge(test_client):

    user_data = {
        "email": "firstInstructorTest@quiz.com",
        "password": "firstInsructorTestPassword"
    }
    response = test_client.post("/api/v1/auth/login", json=user_data)
    content_dict = response.json()

    # Access the access_token
    token = content_dict["access_token"]


    # Multiple Payload items
    question_payload = [
        {
            "question": {
                "text": "What is the capital of Cameroon?",
                "category_id": 1
            },
            "options": [
                {
                    "answer": "Bamenda",
                    "is_correct": True
                },
                {
                    "answer": "Douala",
                    "is_correct": False
                },
                {
                    "answer": "USA",
                    "is_correct": False
                }
            ]
        },
        {
            "question": {
                "text": "What is the capital of America?",
                "category_id": 1
            },
            "options": [
                {
                    "answer": "Washington DC",
                    "is_correct": True
                },
                {
                    "answer": "Kiev",
                    "is_correct": False
                },
                {
                    "answer": "Atlanta",
                    "is_correct": False
                }
            ]
        }
    ]    


    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send a request to create a question with the authenticated token
    response = test_client.post("/api/v1/questions/", json=question_payload, headers=headers)

    # Send a POST request to create a question

    # Assert that the request was successful
    assert response.status_code == 201

    # Get the response JSON
    question_response = response.json()

    question_payload = question_payload

    return {'question_response':question_response,'question_payload':question_payload}


def test_create_questions_previldge(create_questions_previldge):
    result = create_questions_previldge
    question_response = result['question_response']
    question_payload = result['question_payload']

    # Assert that the created question matches the request payload
    assert question_response == question_payload

    # # Assert that the created options match the request payload
    assert len(question_response) == 2

    for response in question_response:
        assert 'Cameroon' in response['question']['text'] or 'America' in response['question']['text'] , f"Expected text 'Cameroon' or 'America' in question, but got: {response['question']['text']}"

