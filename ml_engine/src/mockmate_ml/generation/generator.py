"""Backward-compatible import for the dataset question retriever."""

from mockmate_ml.retrieval.engine import QuestionRetriever

# Keep the old name available for integrations during the package migration.
QuestionGenerator = QuestionRetriever

__all__ = ["QuestionGenerator", "QuestionRetriever"]
