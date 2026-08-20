import re

from app.core.config import get_settings
from app.core.llm import get_llm
from app.core.smalltalk import is_smalltalk
from app.core.vectorstore import similarity_search_with_score
from app.graph.state import GraphState

_OVERVIEW_RE = re.compile(
    r"\b(what is (this|it|the (document|pdf|file|upload(ed)?( document| pdf| file)?))"
    r"( document| pdf| file)? about|"
    r"what does (this|it) (document|pdf|file|say)|"
    r"(summarize|summarise|give me a summary|tl;?dr|overview) (this|it|of this|of the document)?)\b",
    re.IGNORECASE,
)


def _is_overview_question(question: str) -> bool:
    """Broad 'what is this about' / 'summarize this' questions rarely score
    above the relevance threshold against any single chunk - there's no
    passage that's semantically 'about being a summary'. When a specific
    document is scoped, skip the threshold for these and just hand the model
    the top retrieved chunks instead of failing with NO_CONTEXT."""
    return bool(_OVERVIEW_RE.search(question.strip()))

NO_CONTEXT_ANSWER = (
    "I couldn't find anything relevant to that in the uploaded documents. "
    "Try rephrasing, or upload a document that covers this topic."
)

SMALLTALK_ANSWER = (
    "Hi! I'm Dossier's document assistant. Upload a PDF, DOCX, or text file in the "
    "sidebar, then ask me questions about it — I'll answer using only what's in your "
    "documents and cite the source."
)


def check_smalltalk_node(state: GraphState) -> GraphState:
    return {**state, "answer": SMALLTALK_ANSWER if is_smalltalk(state["question"]) else ""}


def route_after_smalltalk_check(state: GraphState) -> str:
    return "smalltalk" if state["answer"] else "retrieve"

SYSTEM_PROMPT = (
    "You are Dossier, an assistant that answers questions strictly using "
    "the provided document excerpts. Cite the source filename inline like [source: name.pdf] "
    "when you use a fact from it. If the excerpts do not contain the answer, say so plainly "
    "instead of guessing."
)


def retrieve_node(state: GraphState) -> GraphState:
    settings = get_settings()
    document_id = state.get("document_id")
    results = similarity_search_with_score(
        state["question"], k=settings.retrieval_k, document_id=document_id
    )
    skip_threshold = bool(document_id) and _is_overview_question(state["question"])
    sources = [
        {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content, "score": score}
        for doc, score in results
        if skip_threshold or score >= settings.relevance_score_threshold
    ]
    return {**state, "sources": sources}


def generate_node(state: GraphState) -> GraphState:
    context = "\n\n".join(
        f"[{s['source']}]\n{s['content']}" for s in state["sources"]
    )
    history_text = "\n".join(
        f"{turn['role']}: {turn['content']}" for turn in state.get("chat_history", [])[-6:]
    )

    messages = [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            f"Conversation so far:\n{history_text}\n\n"
            f"Document excerpts:\n{context}\n\n"
            f"Question: {state['question']}",
        ),
    ]
    llm = get_llm()
    response = llm.invoke(messages)
    return {**state, "answer": response.content}


def should_generate(state: GraphState) -> str:
    return "generate" if state["sources"] else "end_no_context"


def end_no_context_node(state: GraphState) -> GraphState:
    return {**state, "answer": NO_CONTEXT_ANSWER}
