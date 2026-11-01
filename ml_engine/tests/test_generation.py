import pytest
from pydantic import ValidationError

from mockmate_ml.exceptions import GenerationError
from mockmate_ml.generation.generator import QuestionGenerator
from mockmate_ml.schemas.interview import GenerationRequest


def test_generates_requested_number_of_questions(generator: QuestionGenerator) -> None:
    result = generator.generate(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=2)
    )
    assert len(result.questions) == 2
    assert all(question.reference_answer for question in result.questions)
    assert all(question.key_concepts for question in result.questions)


def test_generated_question_ids_are_unique(generator: QuestionGenerator) -> None:
    result = generator.generate(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=3)
    )
    assert len({question.id for question in result.questions}) == 3


def test_unknown_topic_raises_domain_error(generator: QuestionGenerator) -> None:
    with pytest.raises(GenerationError):
        generator.generate(GenerationRequest(topic="Rust", count=2))


def test_invalid_count_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(topic="Python", count=0)


def test_blank_topic_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(topic="   ")


def test_available_topics_returns_difficulties(generator: QuestionGenerator) -> None:
    topics = generator.available_topics()
    assert "Python Basics" in topics
    assert "Beginner" in topics["Python Basics"]
