from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.documents import DocumentChunkResponse
from app.schemas.messages import MessageResponse


class RAGChatRequest(BaseModel):
    file_id: UUID
    question: str = Field(min_length=1)
    conversation_id: UUID | None = None
    provider: str = Field(default="ollama", pattern="^(openai|ollama)$")
    model: str | None = Field(default=None, max_length=100)
    top_k: int = Field(default=5, ge=1, le=10)


class RAGChatResponse(BaseModel):
    file_id: UUID
    question: str
    answer: str
    provider: str
    model: str
    sources: list[DocumentChunkResponse]
    user_message: MessageResponse | None = None
    assistant_message: MessageResponse | None = None

