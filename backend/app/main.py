from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.api.routes import activity, auth, chat, database_chat, documents, health, policy_chat
from app.core.config import get_settings
from app.db import auth_models, demo_models, policy_models  # noqa: F401 - registers tables
from app.db.session import SessionLocal, init_db
from app.dbchat.seed import seed_demo_data
from app.rbac.seed import seed_policy_documents


class SPAStaticFiles(StaticFiles):
    """Serve the built React app, falling back to index.html for client-side routes."""

    async def get_response(self, path: str, scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as session:
        seed_demo_data(session)
        seed_policy_documents(session)
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(database_chat.router, prefix="/api")
app.include_router(policy_chat.router, prefix="/api")

app.mount("/", SPAStaticFiles(directory="app/static", html=True, check_dir=False), name="static")
