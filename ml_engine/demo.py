
from ml_engine.question_generation.generator import question_generation
from ml_engine.answer_evaluation.evaluator import AnswerEvaluator


def main():

    generator = question_generation(seed=2)

    questions = generator.get_questions(
        topic="Python Basics",
        difficulty="Beginner",
        count=1,
        shuffle=False
    )

    question = questions[0]

    full_question = generator.get_question_for_evaluation(
        question["id"]
    )

    print("\n===== MOCKMATE PYTHON MOCK INTERVIEW =====")

    print("\nTopic:", question["topic"])
    print("Difficulty:", question["difficulty"])

    print("\nQuestion:")
    print(question["question"])

    candidate_answer = input("\nYour answer: ").strip()

    if not candidate_answer:
        print("Please enter an answer.")
        return

    print("\nLoading AI evaluation model...")

    evaluator = AnswerEvaluator()

    result = evaluator.evaluate(
        candidate_answer,
        full_question["reference_answer"],
        full_question["keywords"]
    )

    print("\n===== AI EVALUATION =====")

    print("Semantic Similarity:",
          result["semantic_similarity"], "%")

    print("Keyword Coverage:",
          result["keyword_coverage"], "%")

    print("Final Score:",
          result["final_score"], "%")

    print("Matched Keywords:",
          result["matched_keywords"])

    print("Missing Keywords:",
          result["missing_keywords"])

    print("Feedback:",
          result["feedback"])

    print("\n===== INTERVIEW COMPLETED =====")


if __name__ == "__main__":
    main()
