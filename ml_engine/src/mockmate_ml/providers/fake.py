"""Deterministic provider for tests; never makes network requests."""

from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    def __init__(self, factory: Callable[[str, type[T]], T], name: str = "fake"):
        self._factory = factory
        self._name = name
        self.calls: list[tuple[str, type[BaseModel]]] = []

    @property
    def name(self) -> str:
        return self._name

    def generate_structured(self, prompt: str, response_schema: type[T]) -> T:
        self.calls.append((prompt, response_schema))
        return self._factory(prompt, response_schema)
