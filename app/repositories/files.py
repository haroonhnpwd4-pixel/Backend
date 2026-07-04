from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_user_files(session: AsyncSession, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, user_id, file_name, file_type, storage_url, uploaded_at
            from public.files
            where user_id = :user_id
            order by uploaded_at desc
            """
        ),
        {"user_id": user_id},
    )
    return result.mappings().all()


async def get_user_file(session: AsyncSession, file_id: UUID, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, user_id, file_name, file_type, storage_url, uploaded_at
            from public.files
            where id = :file_id and user_id = :user_id
            limit 1
            """
        ),
        {
            "file_id": file_id,
            "user_id": user_id,
        },
    )
    return result.mappings().first()


async def create_file_record(
    session: AsyncSession,
    *,
    user_id: UUID,
    file_name: str,
    file_type: str,
    storage_url: str,
):
    result = await session.execute(
        text(
            """
            insert into public.files (user_id, file_name, file_type, storage_url)
            values (:user_id, :file_name, :file_type, :storage_url)
            returning id, user_id, file_name, file_type, storage_url, uploaded_at
            """
        ),
        {
            "user_id": user_id,
            "file_name": file_name,
            "file_type": file_type,
            "storage_url": storage_url,
        },
    )
    await session.commit()
    return result.mappings().one()


async def delete_file_record(
    session: AsyncSession,
    *,
    file_id: UUID,
    user_id: UUID,
) -> bool:
    result = await session.execute(
        text(
            """
            delete from public.files
            where id = :file_id and user_id = :user_id
            """
        ),
        {
            "file_id": file_id,
            "user_id": user_id,
        },
    )
    await session.commit()
    return result.rowcount > 0
