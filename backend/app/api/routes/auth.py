from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.activity import log_activity
from app.auth.dependencies import get_current_user
from app.auth.google_oauth import build_authorization_url, exchange_code_for_userinfo, new_state_token
from app.auth.security import COOKIE_NAME, create_access_token, hash_password, verify_password
from app.core.config import get_admin_emails, get_settings
from app.db.auth_models import User
from app.db.session import get_db
from app.schemas import LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

_OAUTH_STATE_COOKIE = "oauth_state"


def _set_auth_cookie(response, user_id: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user_id),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> User:
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if db.query(User).filter(User.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="An account with that email already exists")

    user = User(
        email=email,
        name=payload.name.strip() or email,
        password_hash=hash_password(payload.password),
        is_admin=email in get_admin_emails(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_activity(db, user.id, "register")
    _set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    log_activity(db, user.id, "login", detail="password")
    _set_auth_cookie(response, user.id)
    return user


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/google/login")
def google_login() -> RedirectResponse:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured on this server")

    state = new_state_token()
    response = RedirectResponse(build_authorization_url(state))
    response.set_cookie(
        key=_OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=300,
        path="/",
    )
    return response


@router.get("/google/callback")
def google_callback(request: Request, code: str, state: str, db: Session = Depends(get_db)) -> RedirectResponse:
    expected_state = request.cookies.get(_OAUTH_STATE_COOKIE)
    if not expected_state or expected_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    try:
        profile = exchange_code_for_userinfo(code)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail="Google sign-in failed") from exc

    google_id = profile["sub"]
    email = profile.get("email", "").strip().lower()

    user = db.query(User).filter(User.google_id == google_id).first()
    is_new = False
    if user is None:
        user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            email=email,
            name=profile.get("name", email),
            google_id=google_id,
            avatar_url=profile.get("picture"),
            is_admin=email in get_admin_emails(),
        )
        db.add(user)
        is_new = True
    else:
        user.google_id = google_id
        user.avatar_url = profile.get("picture") or user.avatar_url
    db.commit()
    db.refresh(user)

    log_activity(db, user.id, "register" if is_new else "login", detail="google")

    response = RedirectResponse("/")
    response.delete_cookie(_OAUTH_STATE_COOKIE, path="/")
    _set_auth_cookie(response, user.id)
    return response
