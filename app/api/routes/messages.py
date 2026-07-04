from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.core.database import get_db_session
from app.repositories.conversations import get_conversation
from app.repositories.messages import create_message, list_messages
from app.schemas.messages import MessageCreateRequest, MessageResponse

router = APIRouter(prefix="/messages", tags=["Messages"])


async def ensure_conversation_access(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
):
    conversation = await get_conversation(session, conversation_id, user_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation was not found.",
        )


@router.get("/{conversation_id}", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    await ensure_conversation_access(
        session,
        conversation_id=conversation_id,
        user_id=user_id,
    )
    return await list_messages(session, conversation_id)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    payload: MessageCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    await ensure_conversation_access(
        session,
        conversation_id=payload.conversation_id,
        user_id=user_id,
    )
    return await create_message(
        session,
        conversation_id=payload.conversation_id,
        role=payload.role,
        content=payload.content,
    )

