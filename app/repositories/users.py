from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_email(session: AsyncSession, email: str):
    result = await session.execute(
        text(
            """
            select id, name, email, password_hash
            from public.users
            where lower(email) = lower(:email)
            limit 1
            """
        ),
        {"email": email},
    )
    return result.mappings().first()


async def get_user_by_id(session: AsyncSession, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, name, email
            from public.users
            where id = :user_id
            limit 1
            """
        ),
        {"user_id": user_id},
    )
    return result.mappings().first()


async def get_user_with_password_by_id(session: AsyncSession, user_id: UUID):
    result = await session.execute(
        text(
            """
            select id, name, email, password_hash
            from public.users
            where id = :user_id
            limit 1
            """
        ),
        {"user_id": user_id},
    )
    return result.mappings().first()


async def create_user(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    password_hash: str,
):
    result = await session.execute(
        text(
            """
            insert into public.users (name, email, password_hash)
            values (:name, lower(:email), :password_hash)
            returning id, name, email
            """
        ),
        {
            "name": name,
            "email": email,
            "password_hash": password_hash,
        },
    )
    await session.commit()
    return result.mappings().one()


async def update_user_name(session: AsyncSession, *, user_id: UUID, name: str):
    result = await session.execute(
        text(
            """
            update public.users
            set name = :name
            where id = :user_id
            returning id, name, email
            """
        ),
        {
            "user_id": user_id,
            "name": name,
        },
    )
    await session.commit()
    return result.mappings().first()


async def update_user_password_hash(
    session: AsyncSession,
    *,
    user_id: UUID,
    password_hash: str,
):
    await session.execute(
        text(
            """
            update public.users
            set password_hash = :password_hash
            where id = :user_id
            """
        ),
        {
            "user_id": user_id,
            "password_hash": password_hash,
        },
    )
    await session.commit()
