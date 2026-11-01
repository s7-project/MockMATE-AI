"""Application service coordinating question retrieval and answer evaluation."""

from mockmate_ml.evaluation.evaluator import AnswerEvaluator
from mockmate_ml.retrieval.engine import QuestionRetriever
from mockmate_ml.schemas.interview import (
    EvaluationRequest,
    EvaluationResult,
    GenerationRequest,
    GenerationResult,
)


class InterviewService:
    def __init__(
        self,
        retriever: QuestionRetriever | None = None,
        evaluator: AnswerEvaluator | None = None,
        generator: QuestionRetriever | None = None,
    ) -> None:
        # ``generator`` is retained as a compatibility keyword for Phase 1 callers.
        self.retriever = retriever or generator or QuestionRetriever()
        self.generator = self.retriever
        self.evaluator = evaluator or AnswerEvaluator()

    def create_interview(self, request: GenerationRequest) -> GenerationResult:
        return self.retriever.retrieve(request)

    def evaluate_answer(self, request: EvaluationRequest) -> EvaluationResult:
        return self.evaluator.evaluate(request)
