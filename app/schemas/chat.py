from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    session_id: int | None = None
    question: str = Field(..., min_length=1, max_length=5000)


class ChatSource(BaseModel):
    document_id: int
    chunk_id: int
    filename: str
    page: int | None = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
    session_id: int
    safety_flag: bool


class ChatHistoryMessage(BaseModel):
    id: int
    question: str
    answer: str
    sources: list[dict] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    session_id: int
    messages: list[ChatHistoryMessage]


# Backward-compatible schema name
ChatMessageCreate = ChatMessageRequest