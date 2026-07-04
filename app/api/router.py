from fastapi import APIRouter

from app.api.routes import ai, auth, conversations, documents, files, health, messages, rag

api_router = APIRouter()
api_router.include_router(ai.router)
api_router.include_router(auth.router)
api_router.include_router(conversations.router)
api_router.include_router(documents.router)
api_router.include_router(files.router)
api_router.include_router(messages.router)
api_router.include_router(rag.router)
api_router.include_router(health.router)
