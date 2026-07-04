from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.messages import MessageResponse


class AIChatRequest(BaseModel):
    conversation_id: UUID
    message: str = Field(min_length=1)
    provider: str = Field(default="ollama", pattern="^(openai|ollama)$")
    model: str | None = Field(default=None, max_length=100)


class AIChatResponse(BaseModel):
    conversation_id: UUID
    provider: str
    model: str
    user_message: MessageResponse
    assistant_message: MessageResponse
