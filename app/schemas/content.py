from pydantic import BaseModel, Field


class SocialPostGenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    platform: str = Field(default="linkedin", max_length=50)
    tone: str = Field(default="professional", max_length=100)
    provider: str = Field(default="ollama", pattern="^(openai|ollama)$")
    model: str | None = Field(default=None, max_length=100)


class SocialPostGenerateResponse(BaseModel):
    provider: str
    model: str
    platform: str
    post: str
    hashtags: list[str]


class LearningPlanGenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    level: str = Field(default="beginner", max_length=50)
    duration: str = Field(default="2 weeks", max_length=50)
    provider: str = Field(default="ollama", pattern="^(openai|ollama)$")
    model: str | None = Field(default=None, max_length=100)


class LearningPlanGenerateResponse(BaseModel):
    provider: str
    model: str
    topic: str
    roadmap: list[str]
    assignments: list[str]
    quiz_questions: list[str]

