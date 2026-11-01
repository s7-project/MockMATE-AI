import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Import models so SQLAlchemy registers their tables with Base.metadata.
from app import models  # noqa: F401

# Use a separate in-memory SQLite database for tests.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def auth_headers(setup_database):
    client = setup_database

    email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "API Test User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "TestPassword123!"},
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_get_topics(setup_database, auth_headers):
    response = setup_database.get(
        "/api/interview/topics",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_generate_questions(setup_database, auth_headers):
    response = setup_database.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["questions"]) == 3


def test_evaluate_answer(setup_database, auth_headers):
    questions_response = setup_database.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 1,
        },
    )

    assert questions_response.status_code == 200

    question = questions_response.json()["questions"][0]

    response = setup_database.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={
            "question_id": question["id"],
            "candidate_answer": ("A list is mutable, whereas a tuple is immutable."),
        },
    )

    assert response.status_code == 200

    result = response.json()["result"]

    assert 0 <= result["evaluation"]["final_score"] <= 100


def test_generate_invalid_count(setup_database, auth_headers):
    response = setup_database.post(
        "/api/interview/generate",
        headers=auth_headers,
        json={
            "topic": "Python Basics",
            "difficulty": "Beginner",
            "count": 0,
        },
    )

    assert response.status_code == 422


def test_evaluate_invalid_question(setup_database, auth_headers):
    response = setup_database.post(
        "/api/interview/evaluate",
        headers=auth_headers,
        json={
            "question_id": "INVALID_ID",
            "candidate_answer": "Some answer",
        },
    )

    assert response.status_code == 400


def test_interview_requires_authentication(setup_database):
    response = setup_database.get("/api/interview/topics")

    assert response.status_code == 401
