import re
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_model():

    print("Loading MockMATE evaluation model...")

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print("Evaluation model loaded successfully!")

    return model


class AnswerEvaluator:
    def __init__(self):
        self.model = load_model()

    def calculate_similarity(self, candidate_answer, reference_answer):

        embeddings = self.model.encode(
            [candidate_answer, reference_answer], normalize_embeddings=True
        )

        similarity = float(np.dot(embeddings[0], embeddings[1]))

        return max(0.0, min(1.0, similarity))

    def find_keywords(self, answer, keywords):

        normalized_answer = re.sub(r"\s+", " ", answer.lower())

        matched = []

        for keyword in keywords:
            pattern = r"(?<!\w)" + re.escape(keyword.lower().strip()) + r"(?!\w)"

            if re.search(pattern, normalized_answer):
                matched.append(keyword)

        return matched

    def evaluate(self, candidate_answer, reference_answer, keywords):

        if not candidate_answer.strip():
            raise ValueError("Candidate answer cannot be empty")

        if not reference_answer.strip():
            raise ValueError("Reference answer cannot be empty")

        if not keywords:
            raise ValueError("Keywords cannot be empty")

        similarity = self.calculate_similarity(candidate_answer, reference_answer)

        matched_keywords = self.find_keywords(candidate_answer, keywords)

        keyword_coverage = len(matched_keywords) / len(keywords)

        final_score = (similarity * 0.70 + keyword_coverage * 0.30) * 100

        missing_keywords = [
            keyword for keyword in keywords if keyword not in matched_keywords
        ]

        if similarity >= 0.75 and keyword_coverage >= 0.5:
            feedback = "Good answer! Your response covers the main concepts."

        elif similarity >= 0.55:
            feedback = "Partially correct. Add more relevant details."

        else:
            feedback = (
                "Your answer needs improvement. Review the important Python concepts."
            )

        return {
            "semantic_similarity": round(similarity * 100, 2),
            "keyword_coverage": round(keyword_coverage * 100, 2),
            "final_score": round(final_score, 2),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "feedback": feedback,
        }
