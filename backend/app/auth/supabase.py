"""Supabase Auth token verification for API requests."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()
security = HTTPBearer()


def _looks_like_jwt(value: str) -> bool:
    """Return True when a value appears to be a JWT token string."""
    return value.count(".") == 2


def _normalize_user_payload(payload: dict) -> dict:
    """Map Supabase JWT/User payload to internal user shape."""
    metadata = payload.get("user_metadata") or payload.get("app_metadata") or {}
    uid = payload.get("sub") or payload.get("id")
    return {
        "uid": uid,
        "email": payload.get("email"),
        "name": metadata.get("full_name") or metadata.get("name") or "Gig Worker",
    }


def _verify_with_jwt_secret(token: str) -> dict:
    """Verify Supabase JWT directly using project JWT secret (HS256)."""
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience=settings.supabase_jwt_audience,
            options={"verify_aud": bool(settings.supabase_jwt_audience)},
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase token: {exc}",
        )

    user = _normalize_user_payload(payload)
    if not user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token: missing subject",
        )
    return user


async def _verify_with_userinfo(token: str) -> dict:
    """Verify Supabase token by calling the Auth user endpoint."""
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Supabase auth is not configured. Set SUPABASE_URL and "
                "SUPABASE_ANON_KEY, or SUPABASE_JWT_SECRET."
            ),
        )

    userinfo_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.supabase_anon_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(userinfo_url, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Supabase auth service unavailable: {exc}",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase token",
        )

    payload = response.json()
    user = _normalize_user_payload(payload)
    if not user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token payload",
        )
    return user


async def verify_supabase_token(token: str) -> dict:
    """Verify Supabase bearer token and return normalized user claims."""
    # Prefer online verification when URL + anon key are configured because it
    # supports both legacy HS256 and newer asymmetric Supabase signing setups.
    if settings.supabase_url and settings.supabase_anon_key:
        return await _verify_with_userinfo(token)

    # Fallback for local/offline verification when a real HS256 project secret
    # is explicitly configured.
    if settings.supabase_jwt_secret and not _looks_like_jwt(settings.supabase_jwt_secret):
        return _verify_with_jwt_secret(token)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "Supabase auth misconfigured. Set SUPABASE_URL + SUPABASE_ANON_KEY, "
            "or set SUPABASE_JWT_SECRET to your project JWT signing secret."
        ),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency that extracts and validates Supabase bearer token."""
    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return await verify_supabase_token(token)
