from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    chunk_count: int
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class SourceOut(BaseModel):
    source: str
    content: str
    score: float


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceOut]


class ChatMessageOut(BaseModel):
    role: str
    content: str
    sources: list[SourceOut] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
