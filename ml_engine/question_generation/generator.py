import random

from ml_engine.question_generation.question_bank import question_bank


class question_generation:

    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.questions = question_bank

    def get_questions(
        self,
        topic="Python Basics",
        difficulty="Beginner",
        count=5,
        shuffle=True
    ):

        if count < 1:
            raise ValueError("Question count must be at least 1")

        available_questions = [
            question
            for question in self.questions
            if question["topic"].lower() == topic.lower()
            and question["difficulty"].lower() == difficulty.lower()
        ]

        if not available_questions:
            raise ValueError(
                f"No questions found for {topic} - {difficulty}"
            )

        if shuffle:
            self.random.shuffle(available_questions)

        selected = available_questions[:count]

        return [
            {
                "id": q["id"],
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "question": q["question"]
            }
            for q in selected
        ]

    def get_question_for_evaluation(self, question_id):

        for question in self.questions:
            if question["id"] == question_id:
                return question.copy()

        raise ValueError("Question ID not found")