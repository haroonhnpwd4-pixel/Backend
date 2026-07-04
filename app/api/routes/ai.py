from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import AIProviderError, generate_ai_response
from app.auth.dependencies import get_current_user_id
from app.core.database import get_db_session
from app.repositories.conversations import get_conversation
from app.repositories.messages import create_message, list_messages
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.schemas.blog import BlogGenerateRequest, BlogGenerateResponse
from app.schemas.content import (
    LearningPlanGenerateRequest,
    LearningPlanGenerateResponse,
    SocialPostGenerateRequest,
    SocialPostGenerateResponse,
)
from app.services.blog_service import generate_blog
from app.services.content_service import generate_learning_plan, generate_social_post

router = APIRouter(prefix="/ai", tags=["AI"])


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


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    payload: AIChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    await ensure_conversation_access(
        session,
        conversation_id=payload.conversation_id,
        user_id=user_id,
    )

    previous_messages = await list_messages(session, payload.conversation_id)
    user_message = await create_message(
        session,
        conversation_id=payload.conversation_id,
        role="user",
        content=payload.message,
    )
    ai_messages = [
        {"role": message["role"], "content": message["content"]}
        for message in previous_messages
    ]
    ai_messages.append({"role": "user", "content": payload.message})

    try:
        assistant_content, model = await generate_ai_response(
            provider=payload.provider,
            messages=ai_messages,
            model=payload.model,
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    assistant_message = await create_message(
        session,
        conversation_id=payload.conversation_id,
        role="assistant",
        content=assistant_content,
    )

    return AIChatResponse(
        conversation_id=payload.conversation_id,
        provider=payload.provider,
        model=model,
        user_message=user_message,
        assistant_message=assistant_message,
    )


@router.post("/generate-blog", response_model=BlogGenerateResponse)
async def generate_blog_content(
    payload: BlogGenerateRequest,
    _: UUID = Depends(get_current_user_id),
):
    return await generate_blog(payload)


@router.post("/generate-post", response_model=SocialPostGenerateResponse)
async def generate_social_post_content(
    payload: SocialPostGenerateRequest,
    _: UUID = Depends(get_current_user_id),
):
    return await generate_social_post(payload)


@router.post("/learn", response_model=LearningPlanGenerateResponse)
async def generate_learning_assistant_content(
    payload: LearningPlanGenerateRequest,
    _: UUID = Depends(get_current_user_id),
):
    return await generate_learning_plan(payload)
