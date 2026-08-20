import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.activity import log_activity
from app.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.vectorstore import add_documents
from app.db.auth_models import User
from app.db.models import Document
from app.db.session import get_db
from app.ingestion.loaders import UnsupportedFileType, chunk_documents, load_file
from app.schemas import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Document:
    settings = get_settings()
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext or 'unknown'}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    document_id = str(uuid.uuid4())
    stored_path = os.path.join(settings.upload_dir, f"{document_id}{ext}")

    contents = await file.read()
    with open(stored_path, "wb") as f:
        f.write(contents)

    try:
        raw_docs = load_file(stored_path)
        chunks = chunk_documents(raw_docs, document_id=document_id, filename=file.filename or document_id)
        add_documents(chunks)
    except UnsupportedFileType as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record = Document(
        id=document_id,
        filename=file.filename or document_id,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(contents),
        chunk_count=len(chunks),
        status="processed",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_activity(db, user.id, "document_uploaded", workflow="document_intelligence", detail=record.filename)
    return record


@router.get("", response_model=list[DocumentOut])
def list_documents(
    _user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Document]:
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()
