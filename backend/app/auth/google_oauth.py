import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def new_state_token() -> str:
    return secrets.token_urlsafe(24)


def build_authorization_url(state: str) -> str:
    settings = get_settings()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_userinfo(code: str) -> dict:
    """Exchanges an authorization code for tokens, then fetches the profile.

    Returns a dict with at least `sub`, `email`, `name`, `picture`.
    """
    settings = get_settings()
    with httpx.Client(timeout=10.0) as client:
        token_response = client.post(
            _TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        userinfo_response = client.get(
            _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        return userinfo_response.json()
