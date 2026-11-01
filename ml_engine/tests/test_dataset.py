import json

import pytest
from pydantic import ValidationError

from mockmate_ml.data.loader import (
    ingest_records,
    load_default_dataset,
    load_dataset,
    write_dataset,
)
from mockmate_ml.exceptions import DatasetValidationError
from mockmate_ml.schemas.question import DatasetQuestion, QuestionDataset


def test_default_dataset_loads_and_has_unique_ids() -> None:
    dataset = load_default_dataset()
    assert len(dataset.questions) >= 20
    ids = [item.question_id for item in dataset.questions]
    assert len(ids) == len(set(ids))


def test_question_requires_reference_answer_and_concepts() -> None:
    with pytest.raises(ValidationError):
        DatasetQuestion(
            question_id="bad-1",
            question="Explain Python.",
            topic="Python",
            difficulty="Beginner",
            reference_answer="",
            key_concepts=[],
            source_name="test",
            license="test",
        )


def test_duplicate_question_ids_are_rejected() -> None:
    item = load_default_dataset().questions[0].model_dump(mode="json")
    with pytest.raises(ValidationError, match="unique"):
        QuestionDataset(
            dataset_name="duplicates",
            questions=[item, item],
        )


def test_duplicate_question_text_is_rejected() -> None:
    item = load_default_dataset().questions[0].model_dump(mode="json")
    second = dict(item, question_id="different-id")
    with pytest.raises(ValidationError, match="duplicate"):
        QuestionDataset(dataset_name="duplicates", questions=[item, second])


def test_external_import_requires_provenance() -> None:
    with pytest.raises(DatasetValidationError, match="source_name and license"):
        ingest_records(
            [{"question": "What is Python?", "answer": "A programming language."}],
            dataset_name="External",
        )


def test_external_import_normalizes_common_fields() -> None:
    dataset = ingest_records(
        [{
            "id": "EXT-1",
            "prompt": "What is a primary key in SQL?",
            "answer": "A primary key uniquely identifies each row in a table.",
            "category": "SQL",
            "difficulty": "Beginner",
            "keywords": "primary key, unique, row",
            "source_name": "Example source",
            "license": "CC-BY-4.0",
        }],
        dataset_name="External SQL",
    )
    assert dataset.questions[0].question_id == "EXT-1"
    assert dataset.questions[0].topic == "SQL"
    assert "primary key" in dataset.questions[0].key_concepts


def test_dataset_round_trip(tmp_path) -> None:
    dataset = load_default_dataset()
    target = write_dataset(dataset, tmp_path / "copy.json")
    loaded = load_dataset(target)
    assert len(loaded.questions) == len(dataset.questions)


def test_invalid_json_dataset_raises_domain_error(tmp_path) -> None:
    target = tmp_path / "bad.json"
    target.write_text("{bad", encoding="utf-8")
    with pytest.raises(DatasetValidationError):
        load_dataset(target)



def test_duplicate_detection_normalizes_punctuation() -> None:
    dataset = load_default_dataset()
    item = dataset.questions[0].model_dump(mode="json")
    duplicate = dict(
        item,
        question_id="normalized-duplicate",
        question=item["question"].replace("?", "!!!"),
    )
    with pytest.raises(ValidationError, match="duplicate"):
        QuestionDataset(dataset_name="duplicates", questions=[item, duplicate])



def test_codeprep_style_mcq_record_is_normalized() -> None:
    dataset = ingest_records(
        [{
            "id": "js-mcq-001",
            "technology": "javascript",
            "technologyName": "JavaScript",
            "difficulty": 2,
            "difficultyLabel": "easy",
            "type": "MCQ_SINGLE",
            "tags": ["array-methods"],
            "prompt": "Which method creates a new array from a mapping callback?",
            "answer": {
                "options": [
                    {"id": "a", "text": "map"},
                    {"id": "b", "text": "forEach"},
                ],
                "correctOptionId": "a",
            },
            "explanation": "map returns a new array containing callback results.",
        }],
        dataset_name="CodePrep import test",
        default_source_name="CodePrep",
        default_source_url="https://github.com/codeprepdev/codeprep-questions",
        default_license="CC-BY-4.0",
    )
    question = dataset.questions[0]
    assert question.topic == "JavaScript"
    assert question.difficulty.value == "Beginner"
    assert question.question_type == "multiple_choice"
    assert "Correct answer: map" in question.reference_answer
    assert question.source_name == "CodePrep"
