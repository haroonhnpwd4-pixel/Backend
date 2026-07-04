from pydantic import BaseModel, Field


class BlogGenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    audience: str = Field(default="developers", max_length=100)
    tone: str = Field(default="clear and practical", max_length=100)
    word_count: int = Field(default=700, ge=200, le=2000)
    provider: str = Field(default="ollama", pattern="^(openai|ollama)$")
    model: str | None = Field(default=None, max_length=100)


class BlogGenerateResponse(BaseModel):
    provider: str
    model: str
    title: str
    content: str
    seo_keywords: list[str]
    tags: list[str]

