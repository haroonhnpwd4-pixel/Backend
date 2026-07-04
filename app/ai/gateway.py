from app.core.config import get_settings


class AIProviderError(RuntimeError):
    pass


async def generate_openai_response(
    *,
    messages: list[dict[str, str]],
    model: str | None = None,
) -> tuple[str, str]:
    settings = get_settings()

    if not settings.openai_api_key:
        raise AIProviderError("DEVNEXUS_OPENAI_API_KEY is required.")

    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise AIProviderError("Install OpenAI dependency with: python -m pip install openai") from exc

    selected_model = model or settings.openai_model
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=selected_model,
        messages=messages,
    )

    assistant_content = response.choices[0].message.content
    if not assistant_content:
        raise AIProviderError("AI provider returned an empty response.")

    return assistant_content, selected_model


async def generate_ollama_response(
    *,
    messages: list[dict[str, str]],
    model: str | None = None,
) -> tuple[str, str]:
    settings = get_settings()

    try:
        from ollama import AsyncClient
    except ImportError as exc:
        raise AIProviderError("Install Ollama dependency with: python -m pip install ollama") from exc

    selected_model = model or settings.ollama_model
    headers = {}
    if settings.ollama_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    client = AsyncClient(host=settings.ollama_host, headers=headers or None)
    try:
        response = await client.chat(
            model=selected_model,
            messages=messages,
        )
    except Exception as exc:
        raise AIProviderError(
            "Ollama request failed. Make sure Ollama is running and the model is available."
        ) from exc

    assistant_content = response.message.content
    if not assistant_content:
        raise AIProviderError("Ollama returned an empty response.")

    return assistant_content, selected_model


async def generate_ai_response(
    *,
    provider: str,
    messages: list[dict[str, str]],
    model: str | None = None,
) -> tuple[str, str]:
    if provider == "openai":
        return await generate_openai_response(messages=messages, model=model)

    if provider == "ollama":
        return await generate_ollama_response(messages=messages, model=model)

    raise AIProviderError(f"Unsupported AI provider: {provider}")
