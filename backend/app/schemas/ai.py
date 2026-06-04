from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int | None = None
    chunk_index: int


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[Citation]


class SummaryResponse(BaseModel):
    id: str
    document_id: str
    abstract: str
    key_concepts: list[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuizQuestion(BaseModel):
    type: Literal["mcq", "short_answer"]
    question: str
    options: list[str] = []
    correct: str
    explanation: str


class QuizResponse(BaseModel):
    id: str
    document_id: str
    questions: list[QuizQuestion]
    created_at: datetime

    model_config = {"from_attributes": True}


class QuizAttemptRequest(BaseModel):
    answers: list[str]


class QuizAttemptResponse(BaseModel):
    score: int
    total: int


class Flashcard(BaseModel):
    front: str
    back: str


class FlashcardSetResponse(BaseModel):
    id: str
    document_id: str
    cards: list[Flashcard]
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardDocument(BaseModel):
    id: str
    original_filename: str
    status: str
    created_at: datetime
    chunk_count: int


class DashboardResponse(BaseModel):
    documents: list[DashboardDocument]
    quiz_attempts: int
    average_quiz_score: float | None = None
    flashcard_sets: int
