"""Firebase Admin SDK initialisation and token verification."""

from __future__ import annotations
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

# ── Stub mode flag ────────────────────────────────────────────
# When True, Firebase calls are bypassed (for local dev without creds).
_STUB_MODE = True
_firebase_app = None

security = HTTPBearer()
settings = get_settings()


def _init_firebase():
    """Lazily initialise the Firebase Admin SDK."""
    global _firebase_app, _STUB_MODE

    creds_path = settings.firebase_credentials_path
    if not os.path.exists(creds_path):
        _STUB_MODE = True
        return

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(creds_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        _STUB_MODE = False
    except Exception:
        _STUB_MODE = True


def verify_firebase_token(token: str) -> dict:
    """
    Verify an incoming Firebase ID token.

    In stub mode returns a mock payload so local dev works without Firebase.
    """
    if _STUB_MODE:
        return {
            "uid": "dev-user-001",
            "email": "dev@zorva.in",
            "name": "Dev Worker",
        }

    from firebase_admin import auth as fb_auth

    try:
        decoded = fb_auth.verify_id_token(token)
        return decoded
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {exc}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency that extracts & validates the bearer token."""
    _init_firebase()
    return verify_firebase_token(credentials.credentials)
