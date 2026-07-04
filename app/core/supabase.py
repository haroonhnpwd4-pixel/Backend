from functools import lru_cache

from app.core.config import get_settings


@lru_cache
def get_supabase_client(use_service_role: bool = False):
    settings = get_settings()
    supabase_key = (
        settings.supabase_service_role_key
        if use_service_role
        else settings.supabase_anon_key
    )

    if not settings.supabase_url or not supabase_key:
        raise RuntimeError("Supabase URL and key are required.")

    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Install Supabase dependency with: python -m pip install supabase") from exc

    return create_client(settings.supabase_url, supabase_key)

