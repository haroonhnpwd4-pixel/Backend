from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.core.database import get_db_session
from app.repositories.files import list_user_files
from app.schemas.files import FileResponse
from app.services.file_service import delete_user_file, upload_user_file

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    return await upload_user_file(session, user_id=user_id, upload_file=file)


@router.get("", response_model=list[FileResponse])
async def get_files(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    return await list_user_files(session, user_id)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    was_deleted = await delete_user_file(session, user_id=user_id, file_id=file_id)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File was not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

