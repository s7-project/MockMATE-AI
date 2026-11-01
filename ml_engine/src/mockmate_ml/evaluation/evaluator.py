"""Dependency-light baseline answer evaluator.

Semantic and LLM rubric scoring are intentionally separate optional strategies;
this baseline does not pretend keyword overlap is a complete correctness measure.
"""

import re

from mockmate_ml.schemas.interview import EvaluationRequest, EvaluationResult


class AnswerEvaluator:
    def find_keywords(self, answer: str, keywords: list[str]) -> list[str]:
        normalized = re.sub(r"\s+", " ", answer.casefold())
        return [
            keyword
            for keyword in keywords
            if re.search(
                r"(?<!\w)" + re.escape(keyword.casefold().strip()) + r"(?!\w)",
                normalized,
            )
        ]

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        concepts = request.question.key_concepts
        matched = self.find_keywords(request.candidate_answer, concepts)
        coverage = len(matched) / len(concepts) if concepts else 0.0
        score = round(coverage * 100, 2)
        missing = [concept for concept in concepts if concept not in matched]

        if coverage >= 0.8:
            feedback = "The answer mentions most of the expected concepts. Verify technical accuracy and depth."
        elif coverage >= 0.5:
            feedback = "The answer covers some expected concepts; explain the missing concepts more clearly."
        else:
            feedback = "The answer needs more relevant detail. Address the key concepts listed for this question."

        return EvaluationResult(
            question_id=request.question.id,
            final_score=score,
            keyword_coverage=round(coverage * 100, 2),
            matched_concepts=matched,
            missing_concepts=missing,
            feedback=feedback,
        )
