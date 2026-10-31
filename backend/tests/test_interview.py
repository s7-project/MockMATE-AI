import pytest

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():
    # Register a test user
    client.post(
        "/auth/register",
        json={
            "username": "apitest",
            "email": "apitest@example.com",
            "password": "TestPassword123!",
        },
    )

    # Login
    response = client.post(
        "/auth/login", data={"username": "apitest", "password": "TestPassword123!"}
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_get_topics(auth_headers):
    response = client.get("/api/interview/topics", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_generate_questions(auth_headers):
    response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={"topic": "Python Basics", "difficulty": "Beginner", "count": 3},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["questions"]) > 0


def test_evaluate_answer(auth_headers):
    # First generate a question
    questions_response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={"topic": "Python Basics", "difficulty": "Beginner", "count": 1},
    )

    question = questions_response.json()["questions"][0]

    # Submit an answer
    response = client.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={
            "question_id": question["id"],
            "candidate_answer": (
                "Python is a programming language "
                "that supports object oriented programming."
            ),
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_generate_invalid_count(auth_headers):
    response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={"topic": "Python Basics", "difficulty": "Beginner", "count": 0},
    )

    assert response.status_code == 422


def test_evaluate_invalid_question(auth_headers):
    response = client.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={"question_id": "INVALID_ID", "candidate_answer": "Some answer"},
    )

    assert response.status_code == 400
