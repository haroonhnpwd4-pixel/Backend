from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.supabase import get_supabase_client
from app.repositories.files import create_file_record, delete_file_record, get_user_file

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg"}


def _validate_file_name(file_name: str) -> str:
    clean_name = Path(file_name).name
    extension = Path(clean_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {allowed}",
        )

    return clean_name


async def upload_user_file(
    session: AsyncSession,
    *,
    user_id: UUID,
    upload_file: UploadFile,
):
    settings = get_settings()
    file_name = _validate_file_name(upload_file.filename or "upload")
    file_bytes = await upload_file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024

    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size must be {settings.max_upload_size_mb} MB or less.",
        )

    storage_path = f"{user_id}/{uuid4()}-{file_name}"
    content_type = upload_file.content_type or "application/octet-stream"

    try:
        supabase = get_supabase_client(use_service_role=True)
        supabase.storage.from_(settings.supabase_storage_bucket).upload(
            storage_path,
            file_bytes,
            {"content-type": content_type, "upsert": "false"},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File upload to Supabase Storage failed. Check bucket name and storage permissions.",
        ) from exc

    storage_url = f"{settings.supabase_storage_bucket}/{storage_path}"
    return await create_file_record(
        session,
        user_id=user_id,
        file_name=file_name,
        file_type=content_type,
        storage_url=storage_url,
    )


async def delete_user_file(
    session: AsyncSession,
    *,
    user_id: UUID,
    file_id: UUID,
) -> bool:
    settings = get_settings()
    file_record = await get_user_file(session, file_id, user_id)
    if not file_record:
        return False

    storage_prefix = f"{settings.supabase_storage_bucket}/"
    storage_path = file_record["storage_url"]
    if storage_path.startswith(storage_prefix):
        storage_path = storage_path.removeprefix(storage_prefix)

    try:
        supabase = get_supabase_client(use_service_role=True)
        supabase.storage.from_(settings.supabase_storage_bucket).remove([storage_path])
    except Exception:
        pass

    return await delete_file_record(session, file_id=file_id, user_id=user_id)

