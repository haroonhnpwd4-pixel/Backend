from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_messages(session: AsyncSession, conversation_id: UUID):
    result = await session.execute(
        text(
            """
            select id, conversation_id, role, content, created_at
            from public.messages
            where conversation_id = :conversation_id
            order by created_at asc
            """
        ),
        {"conversation_id": conversation_id},
    )
    return result.mappings().all()


async def create_message(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    role: str,
    content: str,
):
    result = await session.execute(
        text(
            """
            insert into public.messages (conversation_id, role, content)
            values (:conversation_id, :role, :content)
            returning id, conversation_id, role, content, created_at
            """
        ),
        {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        },
    )
    await session.commit()
    return result.mappings().one()

