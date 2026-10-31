
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routers import auth, interview


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="AI Mock Interview API",
    description="Multimodal AI Mock Interview System",
    version="1.0.0",
    lifespan=lifespan
)


# React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Authentication routes
app.include_router(auth.router)
app.include_router(interview.router)


@app.get("/")
def home():

    return {
        "message": "AI Mock Interview Backend Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
