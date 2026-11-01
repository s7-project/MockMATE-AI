"""Compatibility exports for the renamed question retrieval service."""

from mockmate_ml.retrieval.engine import QuestionRetriever

QuestionGenerator = QuestionRetriever

__all__ = ["QuestionGenerator", "QuestionRetriever"]
