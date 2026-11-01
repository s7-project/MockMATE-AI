import pytest
from pydantic import ValidationError

from mockmate_ml.evaluation.evaluator import AnswerEvaluator
from mockmate_ml.generation.generator import QuestionGenerator
from mockmate_ml.schemas.interview import EvaluationRequest, GenerationRequest


def _question():
    result = QuestionGenerator(seed=1).generate(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=20)
    )
    return next(q for q in result.questions if "list and a tuple" in q.question.lower())


def test_keyword_matching_respects_word_boundaries() -> None:
    evaluator = AnswerEvaluator()
    assert evaluator.find_keywords("A list is mutable", ["list", "is", "tuple"]) == [
        "list",
        "is",
    ]


def test_evaluation_reports_missing_concepts() -> None:
    question = _question()
    result = AnswerEvaluator().evaluate(
        EvaluationRequest(question=question, candidate_answer="A list is mutable.")
    )
    assert 0 <= result.final_score <= 100
    assert "tuple" in result.missing_concepts


def test_blank_answer_is_rejected() -> None:
    question = _question()
    with pytest.raises(ValidationError):
        EvaluationRequest(question=question, candidate_answer="   ")
