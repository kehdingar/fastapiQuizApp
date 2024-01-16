import pytest
from app.main import app
from app.api.utils.database import get_db
from app.schemas.result import ResultCreate
from app.models.result import Result


# We have to import create_questions too in order to use create_quiz
# Since create_quiz is dependent on create_questions in test_quizzes.py
from .conftest import TestingSessionLocal
from .test_quizes import create_quiz
from .test_quizes import create_questions


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def create_result():
    with TestingSessionLocal() as session:
    
        result_data = ResultCreate(
            total=2,
            user_id=1,
            quiz_id=1,
            score=1
            )
        test_report = Result(**result_data.model_dump())
              
        session.add(test_report)
        session.commit()
        session.refresh(test_report)


def test_get_result_by_user_id(test_client,get_student_header,create_quiz):


    # The create_quiz fixture parameter will get the quiz created from create_quiz in test_quizzes.py
    quiz_payload = {
        'user_id':1,
        'submission': {'1':"Bamenda",'2':'Washington DC'},
        'quiz_id':1
    }
    # Evaluate submmited questions
    test_client.post(f"/api/v1/quizzes/evaluate",json=quiz_payload)

    headers = get_student_header
    # Test the route
    response = test_client.get("/api/v1/results/user/1",headers=headers)
    for result in response.json():
        assert result["user_id"] == 1
    assert response.status_code == 200    

def test_get_result_by_id(test_client,get_student_header,create_result):
    headers = get_student_header
    # Test the route
    response = test_client.get("/api/v1/results/1",headers=headers)
    assert response.json()["total"] == 2
    assert response.status_code == 200

def test_get_result_by_quiz_id(test_client,get_student_header,create_result):
    headers = get_student_header
    # Test the route
    response = test_client.get(f"/api/v1/results/quiz/{1}",headers=headers)
    assert response.json()["quiz_id"] == 1
    assert response.status_code == 200

