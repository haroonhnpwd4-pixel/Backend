from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.chunk_embeddings import (
    create_chunk_embeddings,
    delete_chunk_embeddings,
)
from app.repositories.file_chunks import list_file_chunks
from app.repositories.files import get_user_file


class EmbeddingProviderError(RuntimeError):
    pass


def get_active_embedding_model() -> str:
    settings = get_settings()
    if settings.embedding_provider == "openai":
        return settings.openai_embedding_model
    return settings.ollama_embedding_model


async def generate_openai_embeddings(texts: list[str]) -> tuple[list[list[float]], str]:
    settings = get_settings()

    if not settings.openai_api_key:
        raise EmbeddingProviderError("DEVNEXUS_OPENAI_API_KEY is required for embeddings.")

    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise EmbeddingProviderError("Install OpenAI dependency with: python -m pip install openai") from exc

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
    except Exception as exc:
        error_code = getattr(exc, "code", None)
        status_code = getattr(exc, "status_code", None)

        if error_code == "insufficient_quota" or status_code == 429:
            raise EmbeddingProviderError(
                "OpenAI embeddings failed because the API key has no available quota. "
                "Check OpenAI billing/credits or use another embedding provider."
            ) from exc

        if status_code == 401:
            raise EmbeddingProviderError(
                "OpenAI embeddings failed because the API key is invalid or unauthorized."
            ) from exc

        raise EmbeddingProviderError("OpenAI embeddings request failed.") from exc

    return [item.embedding for item in response.data], settings.openai_embedding_model


async def generate_ollama_embeddings(texts: list[str]) -> tuple[list[list[float]], str]:
    settings = get_settings()

    try:
        from ollama import AsyncClient
    except ImportError as exc:
        raise EmbeddingProviderError("Install Ollama dependency with: python -m pip install ollama") from exc

    headers = {}
    if settings.ollama_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    client = AsyncClient(host=settings.ollama_host, headers=headers or None)
    try:
        response = await client.embed(
            model=settings.ollama_embedding_model,
            input=texts,
        )
    except Exception as exc:
        raise EmbeddingProviderError(
            "Ollama embeddings failed. Make sure Ollama is running and the embedding model is available."
        ) from exc

    embeddings = response.get("embeddings") if isinstance(response, dict) else response.embeddings
    if not embeddings:
        raise EmbeddingProviderError("Ollama returned no embeddings.")

    return embeddings, settings.ollama_embedding_model


async def generate_text_embeddings(texts: list[str]) -> tuple[list[list[float]], str]:
    settings = get_settings()

    if settings.embedding_provider == "openai":
        return await generate_openai_embeddings(texts)

    if settings.embedding_provider == "ollama":
        return await generate_ollama_embeddings(texts)

    raise EmbeddingProviderError(
        "DEVNEXUS_EMBEDDING_PROVIDER must be either 'openai' or 'ollama'."
    )


async def build_file_embeddings(
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

    chunks = await list_file_chunks(session, file_id)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file has no processed chunks. Run document processing first.",
        )

    try:
        vectors, embedding_model = await generate_text_embeddings(
            [chunk["content"] for chunk in chunks]
        )
    except EmbeddingProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    await delete_chunk_embeddings(session, file_id)
    await create_chunk_embeddings(
        session,
        embeddings=[
            {
                "chunk_id": chunk["id"],
                "embedding_model": embedding_model,
                "embedding": vector,
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ],
    )

    return {
        "file_id": file_id,
        "embedding_model": embedding_model,
        "chunk_count": len(chunks),
    }
