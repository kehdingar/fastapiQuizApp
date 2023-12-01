import pytest
from app.schemas.user import UserCreate
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import Role, User
from app.api.auth import get_password_hash
from app.api.utils.database import get_db
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


        category_data = CategoryCreate(name="BACKEND")
        db_category = Category(**category_data.model_dump())

        category_data_2 = CategoryCreate(name="FRONTEND")
        db_category_2 = Category(**category_data_2.model_dump())

        session.add(db_category)
        session.add(db_category_2)
        session.commit()
        session.refresh(db_category)
        session.refresh(db_category_2)  
        session.refresh(db_user)
        session.refresh(instructor_db_user)      



def tearDown():
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture
def get_instructor_header(test_client):
    user_data = {
        "email": "firstInstructorTest@quiz.com",
        "password": "firstInsructorTestPassword"
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
def get_student_header(test_client):
    user_data = {
        "email": "firstTest@quiz.com",
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

@pytest.fixture
def create_questions(test_client,get_instructor_header):

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

    headers = get_instructor_header

    # Send a request to create a question with the authenticated token
    response = test_client.post("/api/v1/questions/", json=question_payload, headers=headers)
    question_response = response.json()
    return question_response

@pytest.fixture
def create_quiz(test_client,get_instructor_header,create_questions):

    headers = get_instructor_header

    # Create a sample question payload
    payload = {
        "name": "Sample Quiz",
        "category_id":1,
        "question_ids":[1,2]
    }

    # Send a request to create a question with the authenticated token
    response = test_client.post("/api/v1/quizzes/", json=payload, headers=headers)
    return response

def test_create_quiz(create_quiz):
    created_quiz_response = create_quiz
    assert created_quiz_response.status_code == 201

def test_get_quiz_by_id(test_client,create_quiz):
    created_quiz_response = create_quiz
    quiz_data = created_quiz_response.json()
    response = test_client.get(f"/api/v1/quizzes/id/{quiz_data['id']}",)
    assert response.status_code == 200

def test_evaluate_quiz(test_client,create_quiz):
    created_quiz_response = create_quiz
    quiz_data = created_quiz_response.json()
    quiz_payload = {
        'user_id':1,
        'submission': {'1':"Bameda",'2':'Washington DC'},
        'quiz_id': quiz_data['id']
    }
    response = test_client.post(f"/api/v1/quizzes/evaluate",json=quiz_payload)

    assert response.status_code == 201

