import pytest
from app.main import app
from app.api.utils.database import get_db
from .conftest import TestingSessionLocal

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


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


def test_delete_quiz(test_client,create_quiz,get_instructor_header):
    created_quiz_response = create_quiz
    quiz_data = created_quiz_response.json()
    headers = get_instructor_header
    response = test_client.delete(f"/api/v1/quizzes/{quiz_data['id']}", headers=headers)
    assert response.status_code == 200

def test_delete_quiz_no_previledge(test_client,create_quiz,get_student_header):
    created_quiz_response = create_quiz
    quiz_data = created_quiz_response.json()
    headers = get_student_header
    response = test_client.delete(f"/api/v1/quizzes/{quiz_data['id']}", headers=headers)
    assert response.status_code == 403

