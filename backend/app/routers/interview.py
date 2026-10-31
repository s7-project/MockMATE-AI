from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/interview", tags=["Interview"])


# Request schemas


class GenerateRequest(BaseModel):
    topic: str = "Python Basics"
    difficulty: str = "Beginner"
    count: int = Field(default=5, ge=1, le=20)


class EvaluateRequest(BaseModel):
    question_id: str
    candidate_answer: str = Field(min_length=1, max_length=10000)


# Generate interview questions


@router.post("/generate")
def generate_questions(
    request: GenerateRequest, current_user=Depends(get_current_user)
):

    try:
        questions = ml_service.generate_questions(
            topic=request.topic, difficulty=request.difficulty, count=request.count
        )

        return {"success": True, "count": len(questions), "questions": questions}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Evaluate candidate answer


@router.post("/evaluate")
def evaluate_answer(request: EvaluateRequest, current_user=Depends(get_current_user)):

    try:
        result = ml_service.evaluate_answer(
            question_id=request.question_id, candidate_answer=request.candidate_answer
        )

        return {"success": True, "result": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get available topics


@router.get("/topics")
def get_topics(current_user=Depends(get_current_user)):

    return {"success": True, "topics": ml_service.get_available_topics()}
