import os
from functools import lru_cache
from types import SimpleNamespace
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status
import httpx


# Load environment variables from .env if present
load_dotenv()


class MissingSupabaseConfig(Exception):
    pass


@lru_cache(maxsize=1)
def get_supabase_config() -> Dict[str, str]:
    """Fetch Supabase REST config from env.

    Uses the service role if available, otherwise anon.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    api_key = service_key or anon_key
    if not supabase_url or not api_key:
        raise MissingSupabaseConfig(
            "SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set"
        )
    return {"url": supabase_url.rstrip("/"), "api_key": api_key}


async def get_current_user(authorization: Optional[str] = Header(default=None)):
    """Validate Bearer token by calling Supabase Auth REST and return a user-like object."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token")

    cfg = get_supabase_config()
    url = f"{cfg['url']}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": cfg["api_key"],
    }
    async with httpx.AsyncClient(timeout=12) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    data = resp.json()
    # Return an object with attribute access similar to supabase-py user,
    # while also attaching the raw JWT for RLS-enabled PostgREST operations
    user_obj = SimpleNamespace(**data)
    setattr(user_obj, "token", token)
    return user_obj


def profiles_select_by_user_id(user_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return profile rows for a user_id using PostgREST.

    When RLS is enabled and only the anon key is available, pass the user's JWT
    as the Bearer token so policies can evaluate auth.uid().
    """
    cfg = get_supabase_config()
    url = f"{cfg['url']}/rest/v1/profiles?user_id=eq.{user_id}"
    headers = {
        "apikey": cfg["api_key"],
        "Authorization": f"Bearer {token or cfg['api_key']}",
        "Accept": "application/json",
    }
    resp = httpx.get(url, headers=headers, timeout=12)
    resp.raise_for_status()
    return resp.json() or []


def profiles_insert(profile: Dict[str, Any], token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Insert a profile row via PostgREST and return inserted rows.

    When RLS is enabled and only the anon key is available, pass the user's JWT
    as the Bearer token so policies can evaluate auth.uid().
    """
    cfg = get_supabase_config()
    url = f"{cfg['url']}/rest/v1/profiles"
    headers = {
        "apikey": cfg["api_key"],
        "Authorization": f"Bearer {token or cfg['api_key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    resp = httpx.post(url, headers=headers, json=profile, timeout=12)
    resp.raise_for_status()
    return resp.json() if resp.content else []


def profiles_update_by_user_id(user_id: str, updates: Dict[str, Any], token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Update profile(s) by user_id via PostgREST and return rows.

    When RLS is enabled and only the anon key is available, pass the user's JWT
    as the Bearer token so policies can evaluate auth.uid().
    """
    cfg = get_supabase_config()
    url = f"{cfg['url']}/rest/v1/profiles?user_id=eq.{user_id}"
    headers = {
        "apikey": cfg["api_key"],
        "Authorization": f"Bearer {token or cfg['api_key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    resp = httpx.patch(url, headers=headers, json=updates, timeout=12)
    resp.raise_for_status()
    return resp.json() if resp.content else []

