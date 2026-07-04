from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_file_chunks(session: AsyncSession, file_id: UUID) -> None:
    await session.execute(
        text(
            """
            delete from public.file_chunks
            where file_id = :file_id
            """
        ),
        {"file_id": file_id},
    )


async def create_file_chunks(
    session: AsyncSession,
    *,
    file_id: UUID,
    chunks: list[str],
):
    await delete_file_chunks(session, file_id)

    if not chunks:
        await session.commit()
        return []

    rows = []
    for chunk_index, content in enumerate(chunks):
        result = await session.execute(
            text(
                """
                insert into public.file_chunks (file_id, chunk_index, content)
                values (:file_id, :chunk_index, :content)
                returning id, file_id, chunk_index, content, created_at
                """
            ),
            {
                "file_id": file_id,
                "chunk_index": chunk_index,
                "content": content,
            },
        )
        rows.append(result.mappings().one())

    await session.commit()
    return rows


async def list_file_chunks(session: AsyncSession, file_id: UUID):
    result = await session.execute(
        text(
            """
            select id, file_id, chunk_index, content, created_at
            from public.file_chunks
            where file_id = :file_id
            order by chunk_index asc
            """
        ),
        {"file_id": file_id},
    )
    return result.mappings().all()
