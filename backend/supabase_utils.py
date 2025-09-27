import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status
from supabase import Client, create_client


# Load environment variables from .env if present
load_dotenv()


class MissingSupabaseConfig(Exception):
    pass


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create and memoize the Supabase client.

    Requires `SUPABASE_URL` and `SUPABASE_ANON_KEY` to be set in the environment.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise MissingSupabaseConfig(
            "SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set"
        )

    return create_client(supabase_url, supabase_key)


async def get_current_user(authorization: Optional[str] = Header(default=None)):
    """FastAPI dependency that validates the Bearer token with Supabase and returns the user.

    It uses Supabase Auth's `get_user` endpoint so we don't need to verify JWTs locally.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token")

    client = get_supabase_client()
    try:
        res = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = getattr(res, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


