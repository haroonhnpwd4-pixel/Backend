from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: UUID
    file_id: UUID
    chunk_index: int
    content: str
    created_at: datetime


class DocumentProcessResponse(BaseModel):
    file_id: UUID
    file_name: str
    chunk_count: int
    chunks: list[DocumentChunkResponse]

