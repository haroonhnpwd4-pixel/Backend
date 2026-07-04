from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.supabase import get_supabase_client
from app.repositories.file_chunks import create_file_chunks, list_file_chunks
from app.repositories.files import get_user_file

TEXT_EXTENSIONS = {".txt", ".csv"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150


def _storage_path(storage_url: str) -> str:
    settings = get_settings()
    storage_prefix = f"{settings.supabase_storage_bucket}/"
    if storage_url.startswith(storage_prefix):
        return storage_url.removeprefix(storage_prefix)
    return storage_url


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document

    document = Document(BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_text(file_name: str, file_bytes: bytes) -> str:
    extension = Path(file_name).suffix.lower()

    if extension in TEXT_EXTENSIONS:
        return file_bytes.decode("utf-8", errors="ignore")

    if extension == ".pdf":
        return _extract_text_from_pdf(file_bytes)

    if extension == ".docx":
        return _extract_text_from_docx(file_bytes)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Only PDF, DOCX, TXT, and CSV files can be processed for document chat.",
    )


def _chunk_text(text: str) -> list[str]:
    normalized_text = " ".join(text.split())
    if not normalized_text:
        return []

    chunks = []
    start = 0
    while start < len(normalized_text):
        end = start + CHUNK_SIZE
        chunks.append(normalized_text[start:end])
        start = end - CHUNK_OVERLAP

    return chunks


async def process_user_document(
    session: AsyncSession,
    *,
    user_id: UUID,
    file_id: UUID,
):
    file_record = await get_user_file(session, file_id, user_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File was not found.",
        )

    extension = Path(file_record["file_name"]).suffix.lower()
    if extension not in DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, TXT, and CSV files can be processed.",
        )

    settings = get_settings()
    try:
        supabase = get_supabase_client(use_service_role=True)
        file_bytes = supabase.storage.from_(settings.supabase_storage_bucket).download(
            _storage_path(file_record["storage_url"])
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to download file from Supabase Storage.",
        ) from exc

    text = _extract_text(file_record["file_name"], file_bytes)
    chunks = _chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text was found in this file.",
        )

    stored_chunks = await create_file_chunks(session, file_id=file_id, chunks=chunks)
    return file_record, stored_chunks


async def get_user_document_chunks(
    session: AsyncSession,
    *,
    user_id: UUID,
    file_id: UUID,
):
    file_record = await get_user_file(session, file_id, user_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File was not found.",
        )

    return await list_file_chunks(session, file_id)

