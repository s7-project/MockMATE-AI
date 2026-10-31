
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():

    email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    # Register test user
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "API Test User",
            "email": email,
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Login using JSON
    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_get_topics(auth_headers):

    response = client.get(
        "/api/interview/topics",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_generate_questions(auth_headers):

    response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 3
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["questions"]) == 3


def test_evaluate_answer(auth_headers):

    questions_response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 1
        }
    )

    assert questions_response.status_code == 200

    question = questions_response.json()["questions"][0]

    response = client.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={
            "question_id": question["id"],
            "candidate_answer": (
                "A list is mutable, whereas a tuple is immutable."
            )
        }
    )

    assert response.status_code == 200

    result = response.json()["result"]

    assert result["evaluation"]["final_score"] >= 0
    assert result["evaluation"]["final_score"] <= 100


def test_generate_invalid_count(auth_headers):

    response = client.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 0
        }
    )

    assert response.status_code == 422


def test_evaluate_invalid_question(auth_headers):

    response = client.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={
            "question_id": "INVALID_ID",
            "candidate_answer": "Some answer"
        }
    )

    assert response.status_code == 400


def test_interview_requires_authentication():

    response = client.get("/api/interview/topics")

    assert response.status_code == 401

