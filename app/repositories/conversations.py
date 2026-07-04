from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_conversations(session: AsyncSession, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, user_id, title, model, created_at
            from public.conversations
            where user_id = :user_id
            order by created_at desc
            """
        ),
        {"user_id": user_id},
    )
    return result.mappings().all()


async def get_conversation(session: AsyncSession, conversation_id: UUID, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, user_id, title, model, created_at
            from public.conversations
            where id = :conversation_id and user_id = :user_id
            limit 1
            """
        ),
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
        },
    )
    return result.mappings().first()


async def create_conversation(
    session: AsyncSession,
    *,
    user_id: UUID,
    title: str,
    model: str,
):
    result = await session.execute(
        text(
            """
            insert into public.conversations (user_id, title, model)
            values (:user_id, :title, :model)
            returning id, user_id, title, model, created_at
            """
        ),
        {
            "user_id": user_id,
            "title": title,
            "model": model,
        },
    )
    await session.commit()
    return result.mappings().one()


async def update_conversation_title(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
    title: str,
):
    result = await session.execute(
        text(
            """
            update public.conversations
            set title = :title
            where id = :conversation_id and user_id = :user_id
            returning id, user_id, title, model, created_at
            """
        ),
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "title": title,
        },
    )
    await session.commit()
    return result.mappings().first()


async def delete_conversation(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
) -> bool:
    result = await session.execute(
        text(
            """
            delete from public.conversations
            where id = :conversation_id and user_id = :user_id
            """
        ),
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
        },
    )
    await session.commit()
    return result.rowcount > 0

