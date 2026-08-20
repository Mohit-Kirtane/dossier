from fastapi import APIRouter, HTTPException

from app.core.errors import friendly_llm_error
from app.dbchat.schema_info import get_schema_summary
from app.dbchat.workflow import run_workflow
from app.schemas import DbChatRequest, DbChatResponse, SchemaTableOut

router = APIRouter(prefix="/database-chat", tags=["database-chat"])


@router.get("/schema", response_model=list[SchemaTableOut])
def schema() -> list[dict]:
    return get_schema_summary()


@router.post("", response_model=DbChatResponse)
def chat(payload: DbChatRequest) -> DbChatResponse:
    try:
        result = run_workflow(payload.question)
    except Exception as exc:  # noqa: BLE001 - translated to a safe, friendly message
        raise HTTPException(status_code=503, detail=friendly_llm_error(exc)) from exc
    return DbChatResponse(
        sql=result["sql"],
        columns=result["columns"],
        rows=result["rows"],
        answer=result["answer"],
    )
