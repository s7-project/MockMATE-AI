import pytest

from mockmate_ml.generation.generator import QuestionGenerator


@pytest.fixture
def generator() -> QuestionGenerator:
    return QuestionGenerator(seed=7)
