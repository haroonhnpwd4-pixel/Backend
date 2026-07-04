from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New Chat", min_length=1, max_length=120)
    model: str = Field(default="gpt", min_length=1, max_length=50)


class ConversationUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    model: str
    created_at: datetime

