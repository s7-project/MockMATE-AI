"""Validated request and response models for interview workflows."""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Difficulty(StrEnum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class InterviewType(StrEnum):
    TECHNICAL = "Technical"
    BEHAVIOURAL = "Behavioural"
    MIXED = "Mixed"


class GenerationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    topic: str = Field(min_length=2, max_length=120)
    difficulty: Difficulty = Difficulty.BEGINNER
    count: int = Field(default=5, ge=1, le=30)
    interview_type: InterviewType = InterviewType.TECHNICAL
    role: str | None = Field(default=None, max_length=120)
    experience_years: float | None = Field(default=None, ge=0, le=50)

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("topic cannot be blank")
        return value


class EvaluationCriterion(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)
    weight: float = Field(gt=0, le=1)


class InterviewQuestion(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=10, max_length=2000)
    topic: str = Field(min_length=2, max_length=120)
    difficulty: Difficulty
    question_type: str = "conceptual"
    reference_answer: str = Field(min_length=10, max_length=6000)
    key_concepts: list[str] = Field(min_length=1, max_length=20)
    evaluation_rubric: list[EvaluationCriterion] = Field(default_factory=list)


class GenerationResult(BaseModel):
    interview_id: UUID = Field(default_factory=uuid4)
    questions: list[InterviewQuestion] = Field(min_length=1)
    provider: str = "question_bank"
    generation_mode: str = "fallback"


class EvaluationRequest(BaseModel):
    question: InterviewQuestion
    candidate_answer: str = Field(min_length=1, max_length=10000)

    @field_validator("candidate_answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("candidate_answer cannot be blank")
        return value.strip()


class EvaluationResult(BaseModel):
    question_id: UUID
    final_score: float = Field(ge=0, le=100)
    keyword_coverage: float = Field(ge=0, le=100)
    matched_concepts: list[str]
    missing_concepts: list[str]
    feedback: str
    evaluation_mode: str = "baseline"
