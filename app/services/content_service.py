import json

from fastapi import HTTPException, status

from app.ai.gateway import AIProviderError, generate_ai_response
from app.schemas.content import (
    LearningPlanGenerateRequest,
    LearningPlanGenerateResponse,
    SocialPostGenerateRequest,
    SocialPostGenerateResponse,
)


def _parse_json_response(raw_content: str, fallback: dict) -> dict:
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError:
        return fallback


async def generate_social_post(
    payload: SocialPostGenerateRequest,
) -> SocialPostGenerateResponse:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a social media copywriter. Return only valid JSON with keys: "
                "post and hashtags. hashtags must be an array of strings."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create a {payload.platform} post about: {payload.topic}\n"
                f"Tone: {payload.tone}"
            ),
        },
    ]

    try:
        raw_content, selected_model = await generate_ai_response(
            provider=payload.provider,
            model=payload.model,
            messages=messages,
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    parsed = _parse_json_response(raw_content, {"post": raw_content, "hashtags": []})
    return SocialPostGenerateResponse(
        provider=payload.provider,
        model=selected_model,
        platform=payload.platform,
        post=str(parsed.get("post") or raw_content),
        hashtags=[str(hashtag) for hashtag in parsed.get("hashtags", [])],
    )


async def generate_learning_plan(
    payload: LearningPlanGenerateRequest,
) -> LearningPlanGenerateResponse:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a technical learning mentor. Return only valid JSON with keys: "
                "roadmap, assignments, quiz_questions. Each value must be an array of strings."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create a learning plan for: {payload.topic}\n"
                f"Level: {payload.level}\n"
                f"Duration: {payload.duration}"
            ),
        },
    ]

    try:
        raw_content, selected_model = await generate_ai_response(
            provider=payload.provider,
            model=payload.model,
            messages=messages,
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    parsed = _parse_json_response(
        raw_content,
        {
            "roadmap": [raw_content],
            "assignments": [],
            "quiz_questions": [],
        },
    )
    return LearningPlanGenerateResponse(
        provider=payload.provider,
        model=selected_model,
        topic=payload.topic,
        roadmap=[str(item) for item in parsed.get("roadmap", [])],
        assignments=[str(item) for item in parsed.get("assignments", [])],
        quiz_questions=[str(item) for item in parsed.get("quiz_questions", [])],
    )

