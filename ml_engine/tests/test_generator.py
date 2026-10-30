import unittest

from ml_engine.question_generation.generator import QuestionGenerator


class TestQuestionGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = QuestionGenerator(seed=42)

    def test_get_beginner_questions(self):

        questions = self.generator.get_questions(
            topic="Python Basics",
            difficulty="Beginner",
            count=2
        )

        self.assertEqual(len(questions), 2)

    def test_question_fields(self):

        questions = self.generator.get_questions(
            topic="OOP",
            difficulty="Intermediate",
            count=1
        )

        self.assertIn("id", questions[0])
        self.assertIn("question", questions[0])
        self.assertIn("topic", questions[0])

    def test_invalid_topic(self):

        with self.assertRaises(ValueError):

            self.generator.get_questions(
                topic="Java",
                difficulty="Beginner",
                count=2
            )

    def test_get_reference_answer(self):

        question = self.generator.get_question_for_evaluation(
            "PY002"
        )

        self.assertIn(
            "mutable",
            question["reference_answer"].lower()
        )


if __name__ == "__main__":
    unittest.main()