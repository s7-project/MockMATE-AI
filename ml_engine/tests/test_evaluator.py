import unittest

from unittest.mock import patch

from ml_engine.answer_evaluation.evaluator import AnswerEvaluator


class TestAnswerEvaluator(unittest.TestCase):

    def setUp(self):

        with patch.object(
            AnswerEvaluator,
            "__init__",
            lambda self: None
        ):
            self.evaluator = AnswerEvaluator()

    def test_keyword_matching(self):

        keywords = [
            "list",
            "tuple",
            "mutable",
            "immutable"
        ]

        answer = (
            "A list is mutable, while a tuple is immutable."
        )

        matched = self.evaluator.find_keywords(
            answer,
            keywords
        )

        self.assertEqual(
            matched,
            ["list", "tuple", "mutable", "immutable"]
        )

    def test_missing_keywords(self):

        keywords = ["list", "tuple", "mutable"]

        answer = "A list and tuple are data structures."

        matched = self.evaluator.find_keywords(
            answer,
            keywords
        )

        self.assertEqual(
            matched,
            ["list", "tuple"]
        )


if __name__ == "__main__":
    unittest.main()