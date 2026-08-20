from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.core.config import get_settings
from app.graph.nodes import (
    check_smalltalk_node,
    end_no_context_node,
    generate_node,
    retrieve_node,
    route_after_smalltalk_check,
    should_generate,
)
from app.graph.state import GraphState


def _tracewell_callbacks() -> list:
    # Tracing must never be able to take Dossier down. If Tracewell is
    # unreachable, misconfigured, or the SDK itself fails to construct (e.g.
    # a local network/SSL issue), skip tracing for this request rather than
    # letting the exception propagate out of run_workflow.
    settings = get_settings()
    if not settings.tracewell_api_key:
        return []
    try:
        from tracewell_sdk import TracewellCallbackHandler

        return [
            TracewellCallbackHandler(
                api_key=settings.tracewell_api_key, base_url=settings.tracewell_base_url
            )
        ]
    except Exception:  # noqa: BLE001 - observability is best-effort, never fatal
        return []


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


def run_workflow(question: str, chat_history: list[dict], document_id: str | None = None) -> GraphState:
    workflow = get_workflow()
    tracewell_handlers = _tracewell_callbacks()
    try:
        result = workflow.invoke(
            {
                "question": question,
                "chat_history": chat_history,
                "document_id": document_id,
                "sources": [],
                "answer": "",
            },
            config={"callbacks": tracewell_handlers},
        )
    except Exception:
        _finish_tracewell_handlers(tracewell_handlers, status="error")
        raise
    _finish_tracewell_handlers(tracewell_handlers, status="complete")
    return result


def _finish_tracewell_handlers(handlers: list, status: str) -> None:
    for handler in handlers:
        try:
            handler.finish(status=status)
        except Exception:  # noqa: BLE001 - observability is best-effort, never fatal
            pass
