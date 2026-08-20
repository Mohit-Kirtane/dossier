import os

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

_EXTENSION_LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
}


class UnsupportedFileType(ValueError):
    pass


class FileTooLarge(ValueError):
    pass


def ensure_within_upload_size_limit(contents: bytes) -> None:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise FileTooLarge(f"File is too large. Maximum size is {settings.max_upload_size_mb} MB.")


def load_file(path: str) -> list[Document]:
    ext = os.path.splitext(path)[1].lower()
    loader_cls = _EXTENSION_LOADERS.get(ext)
    if loader_cls is None:
        raise UnsupportedFileType(f"Unsupported file type: {ext}")
    return loader_cls(path).load()


def chunk_documents(docs: list[Document], document_id: str, filename: str) -> list[Document]:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        chunk.metadata["source"] = filename
    return chunks
