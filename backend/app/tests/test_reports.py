import pytest
from app.schemas.user import UserCreate
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import Role, User
from app.api.auth import get_password_hash
from app.models.result import Result
from app.api.utils.database import get_db
from app.schemas.category import CategoryCreate

# We have to import create_questions too in order to use create_quiz
# Since create_quiz is dependent on create_questions in test_quizzes.py
from .test_quizes import create_questions
from .test_quizes import create_quiz



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

        # Create a user at the beginning of the test - default role is "Student
        user_data = UserCreate(email='firstTest@quiz.com', password=get_password_hash('firstTestPassword'))
        db_user = User(**user_data.model_dump())
        # report_data = ReportCreate()
        test_report = Report(title="Test Report",description="Test desc",user_id=1,quiz_id=1)
        category_data = CategoryCreate(name="BACKEND")
        db_category = Category(**category_data.model_dump())
        category_data_2 = CategoryCreate(name="FRONTEND")
        db_category_2 = Category(**category_data_2.model_dump())          
        session.add(db_user)
        session.add(instructor_db_user)
        session.add(test_report)
        session.add(db_category)
        session.add(db_category_2)            
        session.commit()
        session.refresh(test_report)
        session.refresh(instructor_db_user)
        session.refresh(db_user)
        session.refresh(db_category)
        session.refresh(db_category_2)             

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



def test_get_reports(test_client,get_instructor_header):
    headers = get_instructor_header
    # Test the route
    response = test_client.get("/api/v1/reports",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Report"

def test_unauthorized_get_reports(test_client,get_student_header):
    headers = get_student_header
    # Test the route
    response = test_client.get("/api/v1/reports",headers=headers)
    assert response.status_code == 403


def test_get_report_by_id(test_client,get_student_header):
    headers = get_student_header
    # Test the route
    response = test_client.get("/api/v1/reports/1",headers=headers)
    assert response.json()["title"] == "Test Report"
    assert response.status_code == 200

def test_get_report_by_user_id(test_client,get_student_header,create_quiz):
    quiz_data = create_quiz.json()
    quiz_payload = {
        'user_id':1,
        'submission': {'1':"Bameda",'2':'Washington DC'},
        'quiz_id': quiz_data['id']
    }
    test_client.post(f"/api/v1/quizzes/evaluate",json=quiz_payload)

def test_get_report_by_quiz_id(test_client,get_student_header):
    headers = get_student_header
    quiz_payload = {
        'user_id':1,
        'submission': {'1':"Bameda",'2':'Washington DC'},
        'quiz_id': 1
    }
    test_client.post(f"/api/v1/quizzes/evaluate",json=quiz_payload)

    # Test the route
    response = test_client.get(f"/api/v1/reports/quiz/{1}",headers=headers)
    print(f"\n\nWOW RESULT {response.json()}")
    assert response.json()['result']["quiz_id"] == 1
    assert response.json()['report'] != None
    assert response.status_code == 200