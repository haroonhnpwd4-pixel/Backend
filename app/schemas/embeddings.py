from uuid import UUID

from pydantic import BaseModel


class EmbeddingBuildResponse(BaseModel):
    file_id: UUID
    embedding_model: str
    chunk_count: int

