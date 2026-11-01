"""Provider contracts. Concrete LLM clients implement this protocol."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StructuredLLMProvider(Protocol):
    """Minimal provider contract used by generation and evaluation services."""

    @property
    def name(self) -> str:
        """Human-readable provider identifier."""

    def generate_structured(self, prompt: str, response_schema: type[T]) -> T:
        """Generate and validate an instance of ``response_schema``."""
        ...
