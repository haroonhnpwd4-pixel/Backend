from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import bearer_scheme, decode_access_token
from app.core.database import get_db_session
from app.repositories.users import get_user_by_id
from app.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserUpdateRequest,
    UserResponse,
)
from app.services.auth_service import (
    change_current_user_password,
    login_user,
    register_user,
    update_current_user_name,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    return await register_user(session, payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    return await login_user(session, payload)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    user_id = decode_access_token(credentials.credentials)
    user = await get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user was not found.",
        )

    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    payload: UserUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    user_id = decode_access_token(credentials.credentials)
    return await update_current_user_name(session, user_id=user_id, payload=payload)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    user_id = decode_access_token(credentials.credentials)
    return await change_current_user_password(
        session,
        user_id=user_id,
        payload=payload,
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_db_session),
):
    # This project has no email sender configured yet, so avoid revealing whether
    # the email exists while still providing a working API response for the UI.
    return {
        "message": (
            "If this email is registered, use the backend admin flow or add an "
            "email provider to send password reset links."
        )
    }
