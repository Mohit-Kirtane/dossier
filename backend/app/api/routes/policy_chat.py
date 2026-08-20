import os
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import friendly_llm_error
from app.db.policy_models import PolicyDocument
from app.db.session import get_db
from app.ingestion.loaders import UnsupportedFileType, chunk_documents, load_file
from app.rbac.personas import PERSONAS, ROLES, role_for_persona
from app.rbac.vectorstore import add_policy_documents
from app.rbac.workflow import run_workflow
from app.schemas import PersonaOut, PolicyChatRequest, PolicyChatResponse, PolicyDocumentOut

router = APIRouter(prefix="/policy-chat", tags=["policy-chat"])


@router.get("/personas", response_model=list[PersonaOut])
def personas() -> list[dict]:
    return PERSONAS


@router.get("/documents", response_model=list[PolicyDocumentOut])
def list_documents(persona_id: str, db: Session = Depends(get_db)) -> list[PolicyDocumentOut]:
    role = role_for_persona(persona_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Unknown persona")

    records = db.query(PolicyDocument).order_by(PolicyDocument.uploaded_at.desc()).all()
    return [
        PolicyDocumentOut.model_validate(
            {
                "id": r.id,
                "filename": r.filename,
                "allowed_roles": r.allowed_roles,
                "chunk_count": r.chunk_count,
                "uploaded_at": r.uploaded_at,
                "visible": role in r.allowed_roles,
            }
        )
        for r in records
    ]


@router.post("/upload", response_model=PolicyDocumentOut)
async def upload_policy_document(
    file: UploadFile,
    allowed_roles: list[str] = Form(...),
    db: Session = Depends(get_db),
) -> PolicyDocument:
    settings = get_settings()
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext or 'unknown'}")

    roles = [r for r in allowed_roles if r in ROLES]
    if not roles:
        raise HTTPException(status_code=400, detail="Select at least one valid role")

    os.makedirs(settings.policy_upload_dir, exist_ok=True)
    document_id = str(uuid.uuid4())
    stored_path = os.path.join(settings.policy_upload_dir, f"{document_id}{ext}")

    contents = await file.read()
    with open(stored_path, "wb") as f:
        f.write(contents)

    try:
        raw_docs = load_file(stored_path)
        chunks = chunk_documents(raw_docs, document_id=document_id, filename=file.filename or document_id)
        for chunk in chunks:
            chunk.metadata["allowed_roles"] = roles
        add_policy_documents(chunks)
    except UnsupportedFileType as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record = PolicyDocument(
        id=document_id,
        filename=file.filename or document_id,
        allowed_roles=roles,
        chunk_count=len(chunks),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("", response_model=PolicyChatResponse)
def chat(payload: PolicyChatRequest) -> PolicyChatResponse:
    role = role_for_persona(payload.persona_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Unknown persona")

    try:
        result = run_workflow(payload.question, role)
    except Exception as exc:  # noqa: BLE001 - translated to a safe, friendly message
        raise HTTPException(status_code=503, detail=friendly_llm_error(exc)) from exc

    return PolicyChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        role=role,
        restricted=result["restricted"],
    )
