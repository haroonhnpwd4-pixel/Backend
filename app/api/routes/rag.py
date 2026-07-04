from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.core.database import get_db_session
from app.schemas.embeddings import EmbeddingBuildResponse
from app.schemas.rag import RAGChatRequest, RAGChatResponse
from app.services.embedding_service import build_file_embeddings
from app.services.rag_service import answer_document_question

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/files/{file_id}/embeddings", response_model=EmbeddingBuildResponse)
async def build_document_embeddings(
    file_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    return await build_file_embeddings(
        session,
        user_id=user_id,
        file_id=file_id,
    )


@router.post("/chat", response_model=RAGChatResponse)
async def chat_with_document(
    payload: RAGChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    return await answer_document_question(
        session,
        user_id=user_id,
        file_id=payload.file_id,
        question=payload.question,
        conversation_id=payload.conversation_id,
        provider=payload.provider,
        model=payload.model,
        top_k=payload.top_k,
    )
