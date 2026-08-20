from app.core.config import get_settings
from app.core.llm import get_llm
from app.rbac.state import PolicyState
from app.rbac.vectorstore import similarity_search_with_score

NO_CONTEXT_ANSWER = (
    "I couldn't find any policy content relevant to that. Try rephrasing, or upload a "
    "policy document that covers this topic."
)

SYSTEM_PROMPT = (
    "You are Enterprise Knowledge Copilot, answering internal policy questions strictly "
    "using the provided policy excerpts, which have already been filtered to what the "
    "current user's role is permitted to see. Cite the source filename inline like "
    "[source: name.txt] when you use a fact from it. If the excerpts do not contain the "
    "answer, say so plainly instead of guessing."
)


def retrieve_node(state: PolicyState) -> PolicyState:
    settings = get_settings()
    results = similarity_search_with_score(state["question"], k=settings.retrieval_k * 2)
    relevant = [(doc, score) for doc, score in results if score >= settings.relevance_score_threshold]

    accessible = [
        {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content, "score": score}
        for doc, score in relevant
        if state["role"] in doc.metadata.get("allowed_roles", [])
    ][: settings.retrieval_k]

    restricted = not accessible and bool(relevant)
    return {**state, "sources": accessible, "restricted": restricted}


def generate_node(state: PolicyState) -> PolicyState:
    context = "\n\n".join(f"[{s['source']}]\n{s['content']}" for s in state["sources"])
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Current user role: {state['role']}\n\nPolicy excerpts:\n{context}\n\nQuestion: {state['question']}"),
    ]
    llm = get_llm()
    response = llm.invoke(messages)
    return {**state, "answer": response.content}


def restricted_node(state: PolicyState) -> PolicyState:
    return {
        **state,
        "answer": (
            f"That touches policy content outside what the {state['role']} role can access. "
            "Ask someone with the appropriate permissions (e.g. HR or an executive), or "
            "switch to a role that's authorized to view it."
        ),
    }


def no_context_node(state: PolicyState) -> PolicyState:
    return {**state, "answer": NO_CONTEXT_ANSWER}


def route_after_retrieve(state: PolicyState) -> str:
    if state["sources"]:
        return "generate"
    if state["restricted"]:
        return "restricted"
    return "no_context"
