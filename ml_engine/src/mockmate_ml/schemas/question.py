"""Canonical schema for curated and imported interview question datasets."""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mockmate_ml.schemas.interview import Difficulty


class DatasetQuestion(BaseModel):
    """A source question as stored in the reusable question dataset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    question_id: str = Field(min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$"
    )
    question: str = Field(min_length=10, max_length=2000)
    topic: str = Field(min_length=2, max_length=120)
    difficulty: Difficulty
    question_type: str = Field(default="conceptual", min_length=2, max_length=40)
    roles: list[str] = Field(default_factory=list, max_length=20)
    tags: list[str] = Field(default_factory=list, max_length=30)
    reference_answer: str = Field(min_length=10, max_length=6000)
    key_concepts: list[str] = Field(min_length=1, max_length=30)
    source_name: str = Field(min_length=2, max_length=160)
    source_url: str | None = Field(default=None, max_length=1000)
    license: str = Field(min_length=2, max_length=160)
    evaluation_rubric: list[dict[str, str | float]] = Field(default_factory=list)

    @field_validator("roles", "tags", "key_concepts")
    @classmethod
    def clean_string_lists(cls, values: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(v.strip() for v in values if v.strip()))
        return cleaned

    @field_validator("question_type")
    @classmethod
    def normalize_question_type(cls, value: str) -> str:
        return value.strip().casefold().replace(" ", "_")

    @model_validator(mode="after")
    def validate_rubric_weights(self):
        if self.evaluation_rubric:
            total = sum(float(item.get("weight", 0)) for item in self.evaluation_rubric)
            if abs(total - 1.0) > 0.01:
                raise ValueError("evaluation_rubric weights must sum to 1.0")
        return self


class QuestionDataset(BaseModel):
    """Versioned, validated JSON dataset manifest."""

    model_config = ConfigDict(extra="forbid")

    dataset_name: str = Field(min_length=2, max_length=160)
    dataset_version: str = Field(default="1.0.0", min_length=1, max_length=30)
    description: str = Field(default="", max_length=1000)
    questions: list[DatasetQuestion] = Field(min_length=1)

    @model_validator(mode="after")
    def question_ids_must_be_unique(self):
        ids = [question.question_id for question in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question_id values must be unique within a dataset")
        normalized = [normalize_question_text(q.question) for q in self.questions]
        if len(normalized) != len(set(normalized)):
            raise ValueError("duplicate question text found in dataset")
        return self


def normalize_question_text(value: str) -> str:
    """Normalize text for duplicate detection across imported sources."""
    return re.sub(r"\W+", " ", value.casefold()).strip()
