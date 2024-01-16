import pytest
from app.main import app
from app.api.utils.database import get_db
from app.models.report import Report

# We have to import create_questions too in order to use create_quiz
# Since create_quiz is dependent on create_questions in test_quizzes.py
from .test_quizes import create_questions
from .test_quizes import create_quiz
from .conftest import TestingSessionLocal



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def report_data():
    # Define test data
    report_data = {
        "title": "Test Report",
        "description": "Test Description",
        "user_id": 1,
        "quiz_id": 1
    }
    return report_data

@pytest.fixture(autouse=True)
def initial_report():
    with TestingSessionLocal() as session:

        test_report = Report(title="Test Report",description="Test desc",user_id=1,quiz_id=1)

        session.add(test_report)
        session.commit()
        session.refresh(test_report)     

@pytest.fixture
def create_report(test_client,report_data,get_instructor_header):
    headers= get_instructor_header
    report_data = report_data
    response = test_client.post(f"/api/v1/reports/", json=report_data,headers=headers)
    return response 

@pytest.fixture
def create_report_unauthorized(test_client,report_data):
    report_data = report_data
    response = test_client.post(f"/api/v1/reports/", json=report_data)
    return response


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

def test_get_report_by_quiz_id(test_client,get_student_header,create_quiz):
    headers = get_student_header
    quiz_payload = {
        'user_id':1,
        'submission': {'1':"Bameda",'2':'Washington DC'},
        'quiz_id': 1
    }
    test_client.post(f"/api/v1/quizzes/evaluate",json=quiz_payload)

    # Test the route
    response = test_client.get(f"/api/v1/reports/quiz/{1}",headers=headers)
    assert response.json()['result']["quiz_id"] == 1
    assert response.json()['report'] != None
    assert response.status_code == 200

def test_create_report_unauthorised(create_report_unauthorized,report_data):
    response = create_report_unauthorized
    assert response.status_code == 403

# The order of the test parameters matters
# create_quiz has to come before create_report or it will show error quiz not found
def test_create_report(create_quiz,create_report,report_data):
    response = create_report
    created_report = response.json()
    assert response.status_code == 201
    assert created_report["title"] == report_data["title"]
    assert created_report["description"] == report_data["description"]
    assert created_report["user_id"] == report_data["user_id"]
    assert created_report["quiz_id"] == report_data["quiz_id"]   


