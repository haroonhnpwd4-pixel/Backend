from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_chunk_embeddings(session: AsyncSession, file_id: UUID) -> None:
    await session.execute(
        text(
            """
            delete from public.file_chunk_embeddings embeddings
            using public.file_chunks chunks
            where embeddings.chunk_id = chunks.id
              and chunks.file_id = :file_id
            """
        ),
        {"file_id": file_id},
    )


async def create_chunk_embeddings(
    session: AsyncSession,
    *,
    embeddings: list[dict],
):
    rows = []
    for item in embeddings:
        result = await session.execute(
            text(
                """
                insert into public.file_chunk_embeddings (
                    chunk_id,
                    embedding_model,
                    embedding
                )
                values (:chunk_id, :embedding_model, :embedding)
                on conflict (chunk_id, embedding_model)
                do update set embedding = excluded.embedding
                returning id, chunk_id, embedding_model, embedding, created_at
                """
            ),
            item,
        )
        rows.append(result.mappings().one())

    await session.commit()
    return rows


async def list_file_chunk_embeddings(
    session: AsyncSession,
    *,
    file_id: UUID,
    embedding_model: str,
):
    result = await session.execute(
        text(
            """
            select
                chunks.id as chunk_id,
                chunks.file_id,
                chunks.chunk_index,
                chunks.content,
                chunks.created_at,
                embeddings.embedding_model,
                embeddings.embedding
            from public.file_chunks chunks
            join public.file_chunk_embeddings embeddings
              on embeddings.chunk_id = chunks.id
            where chunks.file_id = :file_id
              and embeddings.embedding_model = :embedding_model
            order by chunks.chunk_index asc
            """
        ),
        {
            "file_id": file_id,
            "embedding_model": embedding_model,
        },
    )
    return result.mappings().all()

