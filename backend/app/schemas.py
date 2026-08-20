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


class DbChatRequest(BaseModel):
    question: str


class DbChatResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict]
    answer: str


class SchemaColumnOut(BaseModel):
    name: str
    type: str


class SchemaTableOut(BaseModel):
    table: str
    columns: list[SchemaColumnOut]


class PersonaOut(BaseModel):
    id: str
    name: str
    title: str
    role: str


class PolicyDocumentOut(BaseModel):
    id: str
    filename: str
    allowed_roles: list[str]
    chunk_count: int
    uploaded_at: datetime
    visible: bool = True

    model_config = {"from_attributes": True}


class PolicyChatRequest(BaseModel):
    question: str
    persona_id: str


class PolicySourceOut(BaseModel):
    source: str
    content: str
    score: float


class PolicyChatResponse(BaseModel):
    answer: str
    sources: list[PolicySourceOut]
    role: str
    restricted: bool


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityLogOut(BaseModel):
    id: str
    event_type: str
    workflow: str | None = None
    detail: str | None = None
    created_at: datetime
    user_name: str | None = None
    user_email: str | None = None

    model_config = {"from_attributes": True}
