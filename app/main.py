from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import DatabaseConfigurationError


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.exception_handler(DatabaseConfigurationError)
    async def database_configuration_error_handler(_, exc: DatabaseConfigurationError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc),
                "hint": "Check DEVNEXUS_DATABASE_URL in your .env file.",
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(_, __: SQLAlchemyError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database connection failed.",
                "hint": "Check your Supabase database host, password, and connection string.",
            },
        )

    @app.exception_handler(OSError)
    async def network_error_handler(_, __: OSError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database network connection failed.",
                "hint": "Check whether your Supabase direct database host resolves, or use the Session pooler connection string.",
            },
        )

    return app


app = create_app()
