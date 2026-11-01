import pytest

from mockmate_ml.retrieval.engine import QuestionRetriever


@pytest.fixture
def generator() -> QuestionRetriever:
    return QuestionRetriever(seed=7)
