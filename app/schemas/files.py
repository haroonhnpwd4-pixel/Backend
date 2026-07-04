from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_name: str
    file_type: str
    storage_url: str
    uploaded_at: datetime

