"""Dataset-backed interview question retrieval and selection."""

import random
import re
from uuid import uuid4

from mockmate_ml.data.loader import load_default_dataset
from mockmate_ml.exceptions import GenerationError, ResourceNotFoundError
from mockmate_ml.schemas.interview import (
    EvaluationCriterion,
    GenerationRequest,
    GenerationResult,
    InterviewQuestion,
)
from mockmate_ml.schemas.question import DatasetQuestion, QuestionDataset


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


class QuestionRetriever:
    """Retrieve relevant questions from a validated dataset.

    This component does not generate new text. It filters and ranks existing
    dataset records, then returns them in the public interview schema.
    """

    def __init__(
        self,
        seed: int | None = None,
        dataset: QuestionDataset | None = None,
    ) -> None:
        self._random = random.Random(seed)
        self._dataset = dataset or load_default_dataset()
        self._by_id = {
            question.question_id: question for question in self._dataset.questions
        }

    @property
    def dataset(self) -> QuestionDataset:
        return self._dataset

    def _matches_topic(self, item: DatasetQuestion, requested_topic: str) -> bool:
        wanted = _normalize(requested_topic)
        topic = _normalize(item.topic)
        tag_values = {_normalize(tag) for tag in item.tags}
        return wanted == topic or wanted in topic or wanted in tag_values

    def _score(self, item: DatasetQuestion, request: GenerationRequest) -> int:
        score = 100
        query = _normalize(request.query or "")
        if query:
            haystack = _normalize(
                " ".join([item.question, item.topic, *item.tags, *item.key_concepts])
            )
            query_terms = set(query.split())
            haystack_terms = set(haystack.split())
            overlap = len(query_terms & haystack_terms)
            score += int(30 * overlap / max(1, len(query_terms)))
            if query in haystack:
                score += 20
        if request.role:
            roles = {_normalize(role) for role in item.roles}
            if _normalize(request.role) in roles:
                score += 25
        return score

    def retrieve(self, request: GenerationRequest) -> GenerationResult:
        candidates = [
            item
            for item in self._dataset.questions
            if self._matches_topic(item, request.topic)
            and item.difficulty == request.difficulty
            and (
                not request.role
                or not item.roles
                or _normalize(request.role) in {_normalize(role) for role in item.roles}
            )
            and (
                not request.question_types
                or item.question_type
                in {
                    value.casefold().replace(" ", "_")
                    for value in request.question_types
                }
            )
        ]

        if not candidates:
            raise GenerationError(
                f"No questions match topic='{request.topic}', "
                f"difficulty={request.difficulty.value}, "
                f"role={request.role or 'any'}."
            )

        if len(candidates) < request.count and not request.allow_partial:
            raise GenerationError(
                f"Requested {request.count} questions, but only {len(candidates)} "
                "match the selected topic, difficulty and filters. Reduce count, "
                "broaden the filters, or set allow_partial=true."
            )

        ranked = sorted(
            candidates,
            key=lambda item: (-self._score(item, request), item.question_id),
        )
        # Randomize equal-score groups to vary interview ordering.
        selected: list[DatasetQuestion] = []
        cursor = 0
        while cursor < len(ranked):
            score = self._score(ranked[cursor], request)
            end = cursor + 1
            while end < len(ranked) and self._score(ranked[end], request) == score:
                end += 1
            group = ranked[cursor:end]
            self._random.shuffle(group)
            selected.extend(group)
            cursor = end
        selected = selected[: request.count]

        questions = [
            InterviewQuestion(
                id=uuid4(),
                dataset_question_id=item.question_id,
                question=item.question,
                topic=item.topic,
                difficulty=item.difficulty,
                question_type=item.question_type,
                reference_answer=item.reference_answer,
                key_concepts=item.key_concepts,
                roles=item.roles,
                tags=item.tags,
                source_name=item.source_name,
                evaluation_rubric=[
                    EvaluationCriterion(
                        name=str(criterion["name"]),
                        description=str(criterion["description"]),
                        weight=float(criterion["weight"]),
                    )
                    for criterion in item.evaluation_rubric
                ],
            )
            for item in selected
        ]
        return GenerationResult(
            questions=questions,
            provider="local_json_dataset",
            generation_mode="retrieval",
            dataset_name=self._dataset.dataset_name,
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Compatibility alias; use retrieve() in new code."""
        return self.retrieve(request)

    def get_question(self, question_id: str) -> dict[str, object]:
        """Compatibility lookup by stable dataset question ID."""
        item = self._by_id.get(question_id)
        if item is None:
            raise ResourceNotFoundError(f"Unknown question ID: {question_id}")
        return {
            "id": item.question_id,
            "topic": item.topic,
            "difficulty": item.difficulty.value,
            "question": item.question,
            "reference_answer": item.reference_answer,
            "keywords": item.key_concepts,
        }

    def available_topics(self) -> dict[str, list[str]]:
        topics: dict[str, set[str]] = {}
        for item in self._dataset.questions:
            topics.setdefault(item.topic, set()).add(item.difficulty.value)
        return {topic: sorted(levels) for topic, levels in sorted(topics.items())}

    def dataset_summary(self) -> dict[str, object]:
        return {
            "dataset_name": self._dataset.dataset_name,
            "dataset_version": self._dataset.dataset_version,
            "question_count": len(self._dataset.questions),
            "topics": self.available_topics(),
        }
