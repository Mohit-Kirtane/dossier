import os
import threading

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.core.embeddings import get_embeddings

_lock = threading.Lock()
_store: FAISS | None = None


def _index_files_exist(index_dir: str) -> bool:
    return os.path.exists(os.path.join(index_dir, "index.faiss"))


def get_policy_vectorstore() -> FAISS:
    global _store
    if _store is not None:
        return _store

    with _lock:
        if _store is not None:
            return _store

        settings = get_settings()
        embeddings = get_embeddings()
        os.makedirs(settings.policy_faiss_index_dir, exist_ok=True)

        if _index_files_exist(settings.policy_faiss_index_dir):
            _store = FAISS.load_local(
                settings.policy_faiss_index_dir, embeddings, allow_dangerous_deserialization=True
            )
        else:
            _store = FAISS.from_documents(
                [Document(page_content="", metadata={"bootstrap": True})], embeddings
            )
            _store.save_local(settings.policy_faiss_index_dir)

        return _store


def add_policy_documents(docs: list[Document]) -> None:
    if not docs:
        return
    settings = get_settings()
    store = get_policy_vectorstore()
    with _lock:
        store.add_documents(docs)
        store.save_local(settings.policy_faiss_index_dir)


def _cosine_similarity_from_l2(l2_distance: float) -> float:
    # Embeddings are L2-normalized, so for unit vectors:
    # ||a - b||^2 = 2 - 2*cos(a, b)  =>  cos(a, b) = 1 - ||a - b||^2 / 2
    return 1 - (l2_distance**2) / 2


def similarity_search_with_score(query: str, k: int) -> list[tuple[Document, float]]:
    store = get_policy_vectorstore()
    results = store.similarity_search_with_score(query, k=k)
    return [
        (doc, _cosine_similarity_from_l2(l2_distance))
        for doc, l2_distance in results
        if not doc.metadata.get("bootstrap")
    ]
