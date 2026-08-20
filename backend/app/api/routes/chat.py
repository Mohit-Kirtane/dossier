from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.errors import friendly_llm_error
from app.db.models import ChatMessage, ChatSession
from app.db.session import get_db
from app.graph.workflow import run_workflow
from app.schemas import ChatMessageOut, ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    if payload.session_id:
        session = db.get(ChatSession, payload.session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(title=payload.question[:60])
        db.add(session)
        db.commit()
        db.refresh(session)

    history = [{"role": m.role, "content": m.content} for m in session.messages]

    try:
        result = run_workflow(payload.question, history)
    except Exception as exc:  # noqa: BLE001 - translated to a safe, friendly message
        raise HTTPException(status_code=503, detail=friendly_llm_error(exc)) from exc

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.question))
    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"],
        )
    )
    db.commit()

    return ChatResponse(session_id=session.id, answer=result["answer"], sources=result["sources"])


@router.get("/chat/{session_id}/messages", response_model=list[ChatMessageOut])
def get_messages(session_id: str, db: Session = Depends(get_db)) -> list[ChatMessage]:
    session = db.get(ChatSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session.messages
