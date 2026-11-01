"""Small local smoke test for the ML package (no API keys or model downloads)."""

from mockmate_ml.schemas.interview import EvaluationRequest, GenerationRequest
from mockmate_ml.services.interview_service import InterviewService


def main() -> None:
    service = InterviewService()
    interview = service.create_interview(
        GenerationRequest(topic="Python Basics", difficulty="Beginner", count=2)
    )
    print(f"Generated {len(interview.questions)} fallback questions")
    question = interview.questions[0]
    print(f"\nQ: {question.question}")
    answer = input("Your answer: ")
    result = service.evaluate_answer(
        EvaluationRequest(question=question, candidate_answer=answer)
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
