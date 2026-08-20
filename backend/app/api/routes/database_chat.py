from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.activity import log_activity
from app.auth.dependencies import get_current_user
from app.core.errors import friendly_llm_error
from app.db.auth_models import User
from app.db.session import get_db
from app.dbchat.schema_info import get_schema_summary
from app.dbchat.workflow import run_workflow
from app.schemas import DbChatRequest, DbChatResponse, SchemaTableOut

router = APIRouter(prefix="/database-chat", tags=["database-chat"])


@router.get("/schema", response_model=list[SchemaTableOut])
def schema(_user: User = Depends(get_current_user)) -> list[dict]:
    return get_schema_summary()


@router.post("", response_model=DbChatResponse)
def chat(
    payload: DbChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DbChatResponse:
    try:
        result = run_workflow(payload.question)
    except Exception as exc:  # noqa: BLE001 - translated to a safe, friendly message
        raise HTTPException(status_code=503, detail=friendly_llm_error(exc)) from exc

    log_activity(db, user.id, "question_asked", workflow="database_chat", detail=payload.question[:200])
    return DbChatResponse(
        sql=result["sql"],
        columns=result["columns"],
        rows=result["rows"],
        answer=result["answer"],
    )
