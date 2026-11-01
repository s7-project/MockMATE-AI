from app.services.ml_service import MLService


def test_backend_adapter_generates_and_evaluates_question() -> None:
    service = MLService()
    questions = service.generate_questions("Python Basics", "Beginner", 1)
    assert len(questions) == 1
    question = questions[0]
    result = service.evaluate_answer(question["id"], "Python is a high-level language")
    assert result["question_id"] == question["id"]
    assert "evaluation" in result
