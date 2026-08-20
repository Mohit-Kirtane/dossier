from app.core.config import get_settings
from app.core.llm import get_llm
from app.core.vectorstore import similarity_search_with_score
from app.graph.state import GraphState

NO_CONTEXT_ANSWER = (
    "I couldn't find anything relevant to that in the uploaded documents. "
    "Try rephrasing, or upload a document that covers this topic."
)

SYSTEM_PROMPT = (
    "You are Enterprise Knowledge Copilot, an assistant that answers questions strictly using "
    "the provided document excerpts. Cite the source filename inline like [source: name.pdf] "
    "when you use a fact from it. If the excerpts do not contain the answer, say so plainly "
    "instead of guessing."
)


def retrieve_node(state: GraphState) -> GraphState:
    settings = get_settings()
    results = similarity_search_with_score(state["question"], k=settings.retrieval_k)
    sources = [
        {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content, "score": score}
        for doc, score in results
        if score >= settings.relevance_score_threshold
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
