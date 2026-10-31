from ml_engine.answer_evaluation.evaluator import AnswerEvaluator
from ml_engine.question_generation.generator import QuestionGenerator


class MLService:
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()

    def generate_questions(self, topic="Python Basics", difficulty="Beginner", count=5):
        return self.question_generator.get_questions(
            topic=topic, difficulty=difficulty, count=count
        )

    def evaluate_answer(self, question_id, candidate_answer):

        # Retrieve reference answer internally
        question = self.question_generator.get_question_for_evaluation(question_id)

        result = self.answer_evaluator.evaluate(
            candidate_answer=candidate_answer,
            reference_answer=question["reference_answer"],
            keywords=question["keywords"],
        )

        return {
            "question_id": question_id,
            "question": question["question"],
            "candidate_answer": candidate_answer,
            "evaluation": result,
        }

    def get_available_topics(self):

        topics = {}

        for question in self.question_generator.questions:
            topic = question["topic"]
            difficulty = question["difficulty"]

            if topic not in topics:
                topics[topic] = set()

            topics[topic].add(difficulty)

        return {topic: sorted(difficulties) for topic, difficulties in topics.items()}


# Shared service instance
ml_service = MLService()
