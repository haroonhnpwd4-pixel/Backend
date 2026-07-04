from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    conversation_id: UUID
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

