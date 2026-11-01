import pytest
from pydantic import ValidationError

from mockmate_ml.exceptions import GenerationError
from mockmate_ml.retrieval.engine import QuestionRetriever
from mockmate_ml.schemas.interview import GenerationRequest


def test_retrieves_requested_number_of_questions(generator: QuestionRetriever) -> None:
    result = generator.generate(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=2)
    )
    assert len(result.questions) == 2
    assert all(question.reference_answer for question in result.questions)
    assert all(question.key_concepts for question in result.questions)
    assert result.provider == "local_json_dataset"
    assert result.generation_mode == "retrieval"


def test_dataset_ids_are_stable_and_response_ids_are_unique(
    generator: QuestionRetriever,
) -> None:
    result = generator.generate(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=3)
    )
    assert len({question.dataset_question_id for question in result.questions}) == 3
    assert len({question.id for question in result.questions}) == 3


def test_unknown_topic_raises_domain_error(generator: QuestionRetriever) -> None:
    with pytest.raises(GenerationError, match="No questions match"):
        generator.generate(GenerationRequest(topic="Rust", count=2))


def test_insufficient_questions_is_explicit(generator: QuestionRetriever) -> None:
    with pytest.raises(GenerationError, match="only"):
        generator.generate(
            GenerationRequest(topic="FastAPI", difficulty="Intermediate", count=5)
        )


def test_allow_partial_returns_available_matches(generator: QuestionRetriever) -> None:
    result = generator.generate(
        GenerationRequest(
            topic="FastAPI", difficulty="Intermediate", count=5, allow_partial=True
        )
    )
    assert len(result.questions) == 2


def test_invalid_count_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(topic="Python", count=0)


def test_blank_topic_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(topic="   ")


def test_available_topics_returns_difficulties(generator: QuestionRetriever) -> None:
    topics = generator.available_topics()
    assert "Python Basics" in topics
    assert "Beginner" in topics["Python Basics"]
    assert "Machine Learning" in topics


def test_role_filtering(generator: QuestionRetriever) -> None:
    result = generator.generate(
        GenerationRequest(
            topic="Machine Learning",
            difficulty="Beginner",
            role="ML Engineer",
            count=1,
        )
    )
    assert result.questions[0].topic == "Machine Learning"


def test_query_ranks_relevant_questions(generator: QuestionRetriever) -> None:
    result = generator.generate(
        GenerationRequest(
            topic="Python Basics",
            difficulty="Beginner",
            count=1,
            query="dictionary key value",
        )
    )
    assert result.questions[0].dataset_question_id == "PY003"


def test_question_type_filter(generator: QuestionRetriever) -> None:
    result = generator.retrieve(
        GenerationRequest(
            topic="FastAPI",
            difficulty="Intermediate",
            count=1,
            question_types=["scenario"],
        )
    )
    assert result.questions[0].dataset_question_id == "API003"


def test_topic_prefix_matches_topic_name(generator: QuestionRetriever) -> None:
    result = generator.retrieve(
        GenerationRequest(topic="Python", difficulty="Beginner", count=1)
    )
    assert result.questions[0].topic == "Python Basics"
