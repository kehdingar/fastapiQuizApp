import pytest
from app.api.auth import get_db
from app.main import app
from .conftest import TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_questions_no_previledge(test_client,get_student_header):

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


    headers = get_student_header

    # Send a request to create a question with the authenticated token
    response = test_client.post("/api/v1/questions/", json=question_payload, headers=headers)
    # Assert the response status code
    assert response.status_code == 403
    # Assert the response body
    assert response.json() == {'detail': 'Insufficient privileges'}


@pytest.fixture
def create_questions_previldge(test_client,get_instructor_header):

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

    headers = get_instructor_header

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


def test_get_questions_by_category(test_client,create_questions_previldge,get_instructor_header):
    headers = get_instructor_header

    # Send a request to create a question with the authenticated token
    response_category = test_client.get(f"/api/v1/questions/category/1",headers=headers)
    # Assert the response status code
    assert response_category.status_code == 200


def test_get_question_by_id(test_client,create_questions_previldge,get_instructor_header):

    result = create_questions_previldge
    created_question = result['question_response']


    headers = get_instructor_header

    response = test_client.get(f"/api/v1/questions/2",headers=headers)
    assert response.status_code == 200


def test_update_question(test_client,create_questions_previldge,get_instructor_header):

    result = create_questions_previldge
    created_question = result['question_response']

    headers = get_instructor_header

    payload = {
        'text': "Changed question",
        'category_id': 56
    }

    response = test_client.put(f"/api/v1/questions/1",json=payload, headers=headers)
    assert response.json()['text'] == 'Changed question'
    assert response.json()['category_id'] == 56
    assert response.status_code == 200