"""Application service coordinating question generation and evaluation."""

from mockmate_ml.evaluation.evaluator import AnswerEvaluator
from mockmate_ml.generation.generator import QuestionGenerator
from mockmate_ml.schemas.interview import (
    EvaluationRequest,
    EvaluationResult,
    GenerationRequest,
    GenerationResult,
)


class InterviewService:
    def __init__(
        self,
        generator: QuestionGenerator | None = None,
        evaluator: AnswerEvaluator | None = None,
    ) -> None:
        self.generator = generator or QuestionGenerator()
        self.evaluator = evaluator or AnswerEvaluator()

    def create_interview(self, request: GenerationRequest) -> GenerationResult:
        return self.generator.generate(request)

    def evaluate_answer(self, request: EvaluationRequest) -> EvaluationResult:
        return self.evaluator.evaluate(request)
