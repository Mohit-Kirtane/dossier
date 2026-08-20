from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.db.session import engine
from app.dbchat.nodes import (
    check_intent_node,
    check_smalltalk_node,
    execute_sql_node,
    generate_sql_node,
    give_up_node,
    refuse_write_node,
    route_after_check,
    route_after_intent,
    route_after_smalltalk_check,
    summarize_node,
    validate_sql_node,
)
from app.dbchat.state import DbChatState


@lru_cache
def get_workflow():
    graph = StateGraph(DbChatState)
    graph.add_node("check_smalltalk", check_smalltalk_node)
    graph.add_node("check_intent", check_intent_node)
    graph.add_node("refuse_write", refuse_write_node)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("validate_sql", validate_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("give_up", give_up_node)

    graph.set_entry_point("check_smalltalk")
    graph.add_conditional_edges(
        "check_smalltalk",
        route_after_smalltalk_check,
        {"smalltalk": END, "check_intent": "check_intent"},
    )
    graph.add_conditional_edges(
        "check_intent", route_after_intent, {"blocked": "refuse_write", "allowed": "generate_sql"}
    )
    graph.add_edge("refuse_write", END)
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_conditional_edges(
        "validate_sql",
        route_after_check,
        {"ok": "execute_sql", "retry": "generate_sql", "give_up": "give_up"},
    )
    graph.add_conditional_edges(
        "execute_sql",
        route_after_check,
        {"ok": "summarize", "retry": "generate_sql", "give_up": "give_up"},
    )
    graph.add_edge("summarize", END)
    graph.add_edge("give_up", END)

    return graph.compile()


def run_workflow(question: str) -> DbChatState:
    workflow = get_workflow()
    initial: DbChatState = {
        "question": question,
        "dialect": engine.dialect.name,
        "sql": "",
        "error": None,
        "retries": 0,
        "columns": [],
        "rows": [],
        "answer": "",
    }
    return workflow.invoke(initial)
