"""Compatibility view of the packaged question dataset.

New code should use ``load_default_dataset`` and ``DatasetQuestion``.
"""

from mockmate_ml.data.loader import load_default_dataset

question_bank = [
    {
        "id": item.question_id,
        "topic": item.topic,
        "difficulty": item.difficulty.value,
        "question": item.question,
        "reference_answer": item.reference_answer,
        "keywords": item.key_concepts,
    }
    for item in load_default_dataset().questions
]
