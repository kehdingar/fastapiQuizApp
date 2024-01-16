from app.api.utils.database import get_db
from app.main import app
from .conftest import TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_fetch_all_categories(test_client,initial_data):

    response = test_client.get("/api/v1/categories/")
    # Assert the response status code
    assert response.status_code == 200
    assert len(response.json()) == 2 # Check the length of the list

def test_fetch_all_categories_by_id(test_client,initial_data):

    response = test_client.get("/api/v1/categories/2")
    # Assert the response status code
    assert response.status_code == 200

def test_create_category_unauthorised(test_client):
    # Send a request to create a category without authenticaion
    category_data = {
        "name":"Python",
    }
    response = test_client.post("/api/v1/categories/", json=category_data)
    # Assert the response status code
    assert response.status_code == 403

def test_create_category(test_client,get_instructor_header):
    # Send a request to create a category with authenticaion
    headers = get_instructor_header
    category_data = {
        "name":"Python",
    }
    response = test_client.post("/api/v1/categories/", json=category_data, headers=headers)
    # Assert the response status code
    assert response.status_code == 201
    assert response.json()['name'] == "Python"