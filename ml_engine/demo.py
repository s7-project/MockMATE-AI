from ml_engine.answer_evaluation.evaluator import AnswerEvaluator
from ml_engine.question_generation.generator import QuestionGenerator


def main():

    print("\n===================================")
    print("       MOCKMATE PYTHON INTERVIEW")
    print("===================================")

    topic = input(
        "\nSelect topic "
        "(Python Basics / OOP / Functions / Exception Handling / Advanced Python): "
    ).strip()

    difficulty = input(
        "Select difficulty (Beginner / Intermediate / Advanced): "
    ).strip()

    generator = QuestionGenerator()

    try:
        questions = generator.get_questions(topic=topic, difficulty=difficulty, count=3)

    except ValueError as error:
        print("\nError:", error)
        return

    print("\nYour interview is starting!")

    evaluator = AnswerEvaluator()

    total_score = 0

    for index, question in enumerate(questions, start=1):
        print("\n-----------------------------------")
        print(f"Question {index}")
        print("-----------------------------------")

        print(question["question"])

        candidate_answer = input("\nYour answer: ").strip()

        full_question = generator.get_question_for_evaluation(question["id"])

        try:
            result = evaluator.evaluate(
                candidate_answer,
                full_question["reference_answer"],
                full_question["keywords"],
            )

        except ValueError as error:
            print("Could not evaluate:", error)
            continue

        total_score += result["final_score"]

        print("\n========== AI EVALUATION ==========")

        print("Semantic Similarity:", result["semantic_similarity"], "%")

        print("Keyword Coverage:", result["keyword_coverage"], "%")

        print("Final Score:", result["final_score"], "%")

        print("Matched Keywords:", result["matched_keywords"])

        print("Missing Keywords:", result["missing_keywords"])

        print("Feedback:", result["feedback"])

        print("\nReference Answer:")
        print(full_question["reference_answer"])

    if questions:
        average_score = total_score / len(questions)

        print("\n===================================")
        print("       INTERVIEW COMPLETED")
        print("===================================")

        print(f"Average Score: {average_score:.2f}%")


if __name__ == "__main__":
    main()
