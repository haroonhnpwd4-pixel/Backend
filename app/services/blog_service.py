import json

from fastapi import HTTPException, status

from app.ai.gateway import AIProviderError, generate_ai_response
from app.schemas.blog import BlogGenerateRequest, BlogGenerateResponse


def _build_blog_prompt(payload: BlogGenerateRequest) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are a technical blog writer. Return only valid JSON with keys: "
                "title, content, seo_keywords, tags. seo_keywords and tags must be arrays of strings."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write a blog about: {payload.topic}\n"
                f"Audience: {payload.audience}\n"
                f"Tone: {payload.tone}\n"
                f"Target length: about {payload.word_count} words"
            ),
        },
    ]


def _parse_blog_response(raw_content: str) -> dict:
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned_content)
    except json.JSONDecodeError:
        return {
            "title": "Generated Blog",
            "content": raw_content,
            "seo_keywords": [],
            "tags": [],
        }

    return {
        "title": str(parsed.get("title") or "Generated Blog"),
        "content": str(parsed.get("content") or raw_content),
        "seo_keywords": [str(keyword) for keyword in parsed.get("seo_keywords", [])],
        "tags": [str(tag) for tag in parsed.get("tags", [])],
    }


async def generate_blog(payload: BlogGenerateRequest) -> BlogGenerateResponse:
    try:
        raw_content, selected_model = await generate_ai_response(
            provider=payload.provider,
            model=payload.model,
            messages=_build_blog_prompt(payload),
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    parsed = _parse_blog_response(raw_content)
    return BlogGenerateResponse(
        provider=payload.provider,
        model=selected_model,
        **parsed,
    )

