"""Thin adapter between FastAPI routes and the independent ML package."""

from mockmate_ml.exceptions import ResourceNotFoundError
from mockmate_ml.schemas.interview import EvaluationRequest, GenerationRequest
from mockmate_ml.services.interview_service import InterviewService


class MLService:
    """Preserves the existing backend method contract during migration."""

    def __init__(self, interview_service: InterviewService | None = None) -> None:
        self.interview_service = interview_service or InterviewService()
        self._questions: dict[str, object] = {}

    def generate_questions(
        self, topic: str = "Python Basics", difficulty: str = "Beginner", count: int = 5
    ) -> list[dict[str, object]]:
        result = self.interview_service.create_interview(
            GenerationRequest(topic=topic, difficulty=difficulty, count=count)
        )
        response: list[dict[str, object]] = []
        for question in result.questions:
            question_id = str(question.id)
            self._questions[question_id] = question
            response.append(
                {
                    "id": question_id,
                    "topic": question.topic,
                    "difficulty": question.difficulty.value,
                    "question": question.question,
                    "reference_answer": question.reference_answer,
                    "keywords": question.key_concepts,
                }
            )
        return response

    def evaluate_answer(
        self, question_id: str, candidate_answer: str
    ) -> dict[str, object]:
        question = self._questions.get(question_id)
        if question is None:
            raise ResourceNotFoundError(
                "Question not found in this backend process. Generate the interview again."
            )
        evaluation = self.interview_service.evaluate_answer(
            EvaluationRequest(question=question, candidate_answer=candidate_answer)
        )
        return {
            "question_id": question_id,
            "question": question.question,
            "candidate_answer": candidate_answer,
            "evaluation": evaluation.model_dump(mode="json"),
        }

    def get_available_topics(self) -> dict[str, list[str]]:
        return self.interview_service.generator.available_topics()


# Lightweight initialization: no transformer, audio, or video models are loaded here.
ml_service = MLService()
