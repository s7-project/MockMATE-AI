"""Domain exceptions exposed by the ML package."""


class MockMATEError(Exception):
    """Base exception for expected application-level failures."""


class GenerationError(MockMATEError, ValueError):
    """Raised when a question set cannot be generated or validated."""


class EvaluationError(MockMATEError, ValueError):
    """Raised when an answer cannot be evaluated."""


class ResourceNotFoundError(MockMATEError, ValueError):
    """Raised when a requested interview resource does not exist."""
