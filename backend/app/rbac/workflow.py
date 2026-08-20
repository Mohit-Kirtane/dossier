from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.rbac.nodes import (
    generate_node,
    no_context_node,
    restricted_node,
    retrieve_node,
    route_after_retrieve,
)
from app.rbac.state import PolicyState


@lru_cache
def get_workflow():
    graph = StateGraph(PolicyState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    # Named "access_restricted" (not "restricted") - a node name can't collide
    # with a PolicyState key, and "restricted" is already a state field.
    graph.add_node("access_restricted", restricted_node)
    graph.add_node("no_context", no_context_node)

    graph.set_entry_point("retrieve")
    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {"generate": "generate", "restricted": "access_restricted", "no_context": "no_context"},
    )
    graph.add_edge("generate", END)
    graph.add_edge("access_restricted", END)
    graph.add_edge("no_context", END)

    return graph.compile()


def run_workflow(question: str, role: str) -> PolicyState:
    workflow = get_workflow()
    initial: PolicyState = {
        "question": question,
        "role": role,
        "sources": [],
        "restricted": False,
        "answer": "",
    }
    return workflow.invoke(initial)
