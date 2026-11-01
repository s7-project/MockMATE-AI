"""Load, validate, and normalize MockMATE question datasets."""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mockmate_ml.exceptions import DatasetValidationError
from mockmate_ml.schemas.question import DatasetQuestion, QuestionDataset


def load_dataset(path: str | Path) -> QuestionDataset:
    """Load a versioned JSON dataset and validate its complete contents."""
    dataset_path = Path(path)
    try:
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
        return QuestionDataset.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise DatasetValidationError(
            f"Could not load valid question dataset '{dataset_path}': {exc}"
        ) from exc


def load_default_dataset() -> QuestionDataset:
    """Load the curated dataset shipped inside the installed package."""
    resource = files("mockmate_ml").joinpath(
        "data", "datasets", "technical_questions.json"
    )
    try:
        raw = json.loads(resource.read_text(encoding="utf-8"))
        return QuestionDataset.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise DatasetValidationError(
            f"The packaged MockMATE question dataset is invalid: {exc}"
        ) from exc


def _difficulty_label(record: dict[str, Any]) -> str:
    value = record.get("difficultyLabel") or record.get("difficulty")
    if isinstance(value, int):
        return {
            1: "Beginner",
            2: "Beginner",
            3: "Intermediate",
            4: "Advanced",
            5: "Advanced",
        }.get(value, "Intermediate")
    normalized = str(value or "Intermediate").casefold()
    if normalized in {"intro", "beginner", "easy"}:
        return "Beginner"
    if normalized in {"medium", "intermediate"}:
        return "Intermediate"
    if normalized in {"hard", "advanced", "expert"}:
        return "Advanced"
    return str(value or "Intermediate")


def _question_text(record: dict[str, Any]) -> str:
    """Build the candidate-facing prompt, including code and MCQ options."""
    prompt = (
        record.get("question") or record.get("prompt") or record.get("Question") or ""
    )
    answer = record.get("answer")
    if not isinstance(answer, dict):
        return prompt

    parts = [prompt]
    if answer.get("code"):
        parts.append(f"Code:\n{answer['code']}")
    options = answer.get("options") or []
    if options:
        parts.append(
            "Options:\n"
            + "\n".join(
                f"{option.get('id', '')}. {option.get('text', '')}"
                for option in options
            )
        )
    return "\n\n".join(part for part in parts if part)


def _answer_text(record: dict[str, Any]) -> str:
    """Convert common string and structured answer representations to text."""
    answer = (
        record.get("reference_answer")
        or record.get("answer")
        or record.get("ideal_answer")
        or record.get("Answer")
    )
    explanation = record.get("explanation")
    if isinstance(answer, str):
        result = answer
    elif isinstance(answer, dict):
        parts: list[str] = []
        if answer.get("sampleAnswer"):
            parts.append(str(answer["sampleAnswer"]))
        if answer.get("back"):
            parts.append(str(answer["back"]))
        if answer.get("value") is not None:
            parts.append(f"Correct answer: {answer['value']}")
        options = answer.get("options") or []
        correct_ids = list(answer.get("correctOptionIds") or [])
        if answer.get("correctOptionId"):
            correct_ids.append(answer["correctOptionId"])
        correct_text = [
            str(option.get("text", ""))
            for option in options
            if option.get("id") in correct_ids and option.get("text")
        ]
        if correct_text:
            parts.append("Correct answer: " + "; ".join(correct_text))
        if answer.get("expectedOutput") is not None:
            parts.append(f"Expected output: {answer['expectedOutput']}")
        if answer.get("buggyLines"):
            lines = ", ".join(str(line) for line in answer["buggyLines"])
            parts.append(f"Buggy line numbers: {lines}")
        result = "\n".join(parts)
    else:
        result = ""

    if explanation:
        result = f"{result}\nExplanation: {explanation}".strip()
    return result


def normalize_external_record(
    record: dict[str, Any],
    index: int,
    *,
    default_source_name: str | None = None,
    default_source_url: str | None = None,
    default_license: str | None = None,
) -> dict[str, Any]:
    """Map common external dataset fields to the canonical schema.

    Provenance must come from the source record, source manifest, or explicit
    CLI arguments. The importer never invents a source or a licence.
    """
    question = _question_text(record)
    answer = _answer_text(record)
    concepts = (
        record.get("key_concepts") or record.get("keywords") or record.get("tags") or []
    )
    if isinstance(concepts, str):
        concepts = [part.strip() for part in concepts.split(",") if part.strip()]
    tags = record.get("tags") or []
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(",") if part.strip()]
    roles = record.get("roles") or record.get("role") or []
    if isinstance(roles, str):
        roles = [part.strip() for part in roles.split(",") if part.strip()]

    source_name = record.get("source_name") or default_source_name
    source_url = record.get("source_url") or default_source_url
    license_name = record.get("license") or default_license

    if not question or not answer:
        raise DatasetValidationError(
            f"Record {index} must contain a question and a usable answer."
        )
    if not source_name or not license_name:
        raise DatasetValidationError(
            f"Record {index} must declare source_name and license; "
            "the importer will not invent provenance."
        )

    question_type = record.get("question_type") or record.get("type") or "conceptual"
    type_mapping = {
        "SHORT_ANSWER": "conceptual",
        "FLASHCARD": "conceptual",
        "MCQ_SINGLE": "multiple_choice",
        "MCQ_MULTI": "multiple_choice",
        "TRUE_FALSE": "true_false",
        "CODE_OUTPUT": "coding",
        "FIND_THE_BUG": "debugging",
    }
    question_type = type_mapping.get(str(question_type).upper(), str(question_type))
    topic = (
        record.get("topic")
        or record.get("category")
        or record.get("technologyName")
        or record.get("technology")
        or "Uncategorized"
    )
    return {
        "question_id": str(
            record.get("question_id") or record.get("id") or f"imported-{index:05d}"
        ),
        "question": question,
        "topic": topic,
        "difficulty": _difficulty_label(record),
        "question_type": question_type,
        "roles": roles,
        "tags": tags,
        "reference_answer": answer,
        "key_concepts": concepts,
        "source_name": source_name,
        "source_url": source_url,
        "license": license_name,
        "evaluation_rubric": record.get("evaluation_rubric") or [],
    }


def ingest_records(
    records: list[dict[str, Any]],
    dataset_name: str,
    dataset_version: str = "1.0.0",
    description: str = "Imported and normalized question dataset",
    *,
    default_source_name: str | None = None,
    default_source_url: str | None = None,
    default_license: str | None = None,
) -> QuestionDataset:
    """Normalize external records, then validate the complete dataset."""
    try:
        normalized = [
            DatasetQuestion.model_validate(
                normalize_external_record(
                    record,
                    index,
                    default_source_name=default_source_name,
                    default_source_url=default_source_url,
                    default_license=default_license,
                )
            )
            for index, record in enumerate(records, start=1)
        ]
        return QuestionDataset(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            description=description,
            questions=normalized,
        )
    except (ValidationError, DatasetValidationError) as exc:
        message = f"Imported dataset failed validation: {exc}"
        raise DatasetValidationError(message) from exc


def write_dataset(dataset: QuestionDataset, destination: str | Path) -> Path:
    """Write a validated dataset as UTF-8 JSON."""
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            dataset.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return output
