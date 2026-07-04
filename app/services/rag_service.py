from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import AIProviderError, generate_ai_response
from app.repositories.conversations import get_conversation
from app.repositories.chunk_embeddings import list_file_chunk_embeddings
from app.repositories.file_chunks import list_file_chunks
from app.repositories.files import get_user_file
from app.repositories.messages import create_message
from app.services.embedding_service import (
    EmbeddingProviderError,
    generate_text_embeddings,
    get_active_embedding_model,
)


def _rank_chunks(question: str, chunks, top_k: int):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Install scikit-learn to use RAG retrieval.",
        ) from exc

    documents = [chunk["content"] for chunk in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([question, *documents])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    ranked_indexes = scores.argsort()[::-1][:top_k]

    return [chunks[index] for index in ranked_indexes if scores[index] > 0]


def _cosine_similarity(first: list[float], second: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(first, second, strict=True))
    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if not first_norm or not second_norm:
        return 0
    return dot_product / (first_norm * second_norm)


async def _rank_chunks_by_embeddings(
    session: AsyncSession,
    *,
    file_id: UUID,
    question: str,
    top_k: int,
):
    embedded_chunks = await list_file_chunk_embeddings(
        session,
        file_id=file_id,
        embedding_model=get_active_embedding_model(),
    )
    if not embedded_chunks:
        return []

    try:
        question_vectors, _ = await generate_text_embeddings([question])
    except EmbeddingProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    question_vector = question_vectors[0]
    scored_chunks = [
        (_cosine_similarity(question_vector, chunk["embedding"]), chunk)
        for chunk in embedded_chunks
    ]
    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return [
        {
            "id": chunk["chunk_id"],
            "file_id": chunk["file_id"],
            "chunk_index": chunk["chunk_index"],
            "content": chunk["content"],
            "created_at": chunk["created_at"],
        }
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]


def _build_rag_messages(question: str, sources) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"Source chunk {source['chunk_index']}:\n{source['content']}"
        for source in sources
    )

    return [
        {
            "role": "system",
            "content": (
                "You are a document question-answering assistant. "
                "Answer using only the provided context. "
                "If the answer is not in the context, say you do not know."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}",
        },
    ]


async def answer_document_question(
    session: AsyncSession,
    *,
    user_id: UUID,
    file_id: UUID,
    question: str,
    conversation_id: UUID | None,
    provider: str,
    model: str | None,
    top_k: int,
):
    file_record = await get_user_file(session, file_id, user_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File was not found.",
        )

    user_message = None
    if conversation_id:
        conversation = await get_conversation(session, conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation was not found.",
            )
        user_message = await create_message(
            session,
            conversation_id=conversation_id,
            role="user",
            content=question,
        )

    chunks = await list_file_chunks(session, file_id)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file has no processed chunks. Run document processing first.",
        )

    sources = await _rank_chunks_by_embeddings(
        session,
        file_id=file_id,
        question=question,
        top_k=top_k,
    )
    if not sources:
        sources = _rank_chunks(question, chunks, top_k)
    if not sources:
        sources = chunks[:top_k]

    try:
        answer, selected_model = await generate_ai_response(
            provider=provider,
            model=model,
            messages=_build_rag_messages(question, sources),
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    assistant_message = None
    if conversation_id:
        assistant_message = await create_message(
            session,
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

    return {
        "file_id": file_id,
        "question": question,
        "answer": answer,
        "provider": provider,
        "model": selected_model,
        "sources": sources,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }
