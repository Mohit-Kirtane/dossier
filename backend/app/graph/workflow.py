from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    check_smalltalk_node,
    end_no_context_node,
    generate_node,
    retrieve_node,
    route_after_smalltalk_check,
    should_generate,
)
from app.graph.state import GraphState


@lru_cache
def get_workflow():
    graph = StateGraph(GraphState)
    graph.add_node("check_smalltalk", check_smalltalk_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("end_no_context", end_no_context_node)

    graph.set_entry_point("check_smalltalk")
    graph.add_conditional_edges(
        "check_smalltalk", route_after_smalltalk_check, {"smalltalk": END, "retrieve": "retrieve"}
    )
    graph.add_conditional_edges(
        "retrieve", should_generate, {"generate": "generate", "end_no_context": "end_no_context"}
    )
    graph.add_edge("generate", END)
    graph.add_edge("end_no_context", END)

    return graph.compile()


def run_workflow(question: str, chat_history: list[dict]) -> GraphState:
    workflow = get_workflow()
    return workflow.invoke({"question": question, "chat_history": chat_history, "sources": [], "answer": ""})
