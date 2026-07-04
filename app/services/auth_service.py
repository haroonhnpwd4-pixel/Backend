from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, hash_password, verify_password
from uuid import UUID

from app.repositories.users import (
    create_user,
    get_user_by_email,
    get_user_with_password_by_id,
    update_user_name,
    update_user_password_hash,
)
from app.schemas.auth import (
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserUpdateRequest,
)


async def register_user(
    session: AsyncSession,
    payload: UserRegisterRequest,
) -> TokenResponse:
    existing_user = await get_user_by_email(session, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = await create_user(
        session,
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    access_token = create_access_token(user["id"])

    return TokenResponse(access_token=access_token, user=user)


async def login_user(
    session: AsyncSession,
    payload: UserLoginRequest,
) -> TokenResponse:
    user = await get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(user["id"])

    return TokenResponse(access_token=access_token, user=user)


async def update_current_user_name(
    session: AsyncSession,
    *,
    user_id: UUID,
    payload: UserUpdateRequest,
):
    user = await update_user_name(session, user_id=user_id, name=payload.name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user was not found.",
        )

    return user


async def change_current_user_password(
    session: AsyncSession,
    *,
    user_id: UUID,
    payload: PasswordChangeRequest,
):
    user = await get_user_with_password_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user was not found.",
        )

    if not verify_password(payload.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    await update_user_password_hash(
        session,
        user_id=user_id,
        password_hash=hash_password(payload.new_password),
    )

    return {"message": "Password updated successfully."}
