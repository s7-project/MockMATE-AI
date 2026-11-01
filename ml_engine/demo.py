"""Local smoke test for dataset retrieval and baseline answer evaluation."""

from mockmate_ml.schemas.interview import EvaluationRequest, GenerationRequest
from mockmate_ml.services.interview_service import InterviewService


def main() -> None:
    service = InterviewService()
    interview = service.create_interview(
        GenerationRequest(
            topic="Python Basics",
            difficulty="Beginner",
            count=2,
            role="Python Developer",
        )
    )
    print(
        f"Retrieved {len(interview.questions)} questions from "
        f"{interview.dataset_name} ({interview.generation_mode})"
    )
    question = interview.questions[0]
    print(f"\\nQ: {question.question}")
    answer = input("Your answer: ")
    result = service.evaluate_answer(
        EvaluationRequest(question=question, candidate_answer=answer)
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
