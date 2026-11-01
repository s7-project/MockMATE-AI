"""Question generation with a curated fallback bank.

The provider dependency is optional by design. Phase 2 adds the production LLM
provider and prompt pipeline without changing this public service contract.
"""

import random
from uuid import uuid4

from mockmate_ml.data.question_bank import question_bank
from mockmate_ml.exceptions import GenerationError, ResourceNotFoundError
from mockmate_ml.schemas.interview import (
    Difficulty,
    GenerationRequest,
    GenerationResult,
    InterviewQuestion,
)


class QuestionGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self._bank = question_bank

    def generate(self, request: GenerationRequest) -> GenerationResult:
        matches = [
            item
            for item in self._bank
            if item["topic"].casefold() == request.topic.casefold()
            and item["difficulty"].casefold() == request.difficulty.value.casefold()
        ]
        if not matches:
            raise GenerationError(
                f"No fallback questions for topic '{request.topic}' "
                f"at difficulty '{request.difficulty.value}'."
            )

        self._random.shuffle(matches)
        selected = matches[: request.count]
        questions = [
            InterviewQuestion(
                id=uuid4(),
                question=item["question"],
                topic=item["topic"],
                difficulty=Difficulty(item["difficulty"]),
                reference_answer=item["reference_answer"],
                key_concepts=item["keywords"],
            )
            for item in selected
        ]
        return GenerationResult(questions=questions)

    def get_question(self, legacy_question_id: str) -> dict[str, object]:
        """Temporary compatibility lookup for the existing API integration."""
        for item in self._bank:
            if item["id"] == legacy_question_id:
                return dict(item)
        raise ResourceNotFoundError(f"Unknown question ID: {legacy_question_id}")

    def available_topics(self) -> dict[str, list[str]]:
        topics: dict[str, set[str]] = {}
        for item in self._bank:
            topics.setdefault(item["topic"], set()).add(item["difficulty"])
        return {topic: sorted(levels) for topic, levels in topics.items()}
