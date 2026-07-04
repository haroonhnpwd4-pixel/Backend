from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.core.database import get_db_session
from app.schemas.documents import DocumentChunkResponse, DocumentProcessResponse
from app.services.document_service import (
    get_user_document_chunks,
    process_user_document,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/{file_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    file_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    file_record, chunks = await process_user_document(
        session,
        user_id=user_id,
        file_id=file_id,
    )

    return DocumentProcessResponse(
        file_id=file_id,
        file_name=file_record["file_name"],
        chunk_count=len(chunks),
        chunks=chunks,
    )


@router.get("/{file_id}/chunks", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    file_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    return await get_user_document_chunks(
        session,
        user_id=user_id,
        file_id=file_id,
    )

