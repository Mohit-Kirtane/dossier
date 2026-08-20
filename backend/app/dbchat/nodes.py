import re

from sqlalchemy import text

from app.core.llm import get_llm
from app.db.session import engine
from app.dbchat.schema_info import get_schema_description
from app.dbchat.sql_guard import MAX_ROWS, SqlValidationError, validate_and_prepare_sql
from app.dbchat.state import DbChatState

MAX_RETRIES = 1

_WRITE_INTENT_RE = re.compile(
    r"\b(delete|remove|drop|truncate|update|insert|add\s+a\s+\w+|create\s+a\s+\w+|"
    r"modify|change\s+the|alter|set\s+\w+\s*=)\b",
    re.IGNORECASE,
)

REFUSAL_MESSAGE = (
    "This assistant only runs read-only queries — it can't delete, update, insert, or "
    "otherwise change data. Try asking a question about the existing data instead."
)

GENERATE_SYSTEM_PROMPT = (
    "You translate natural-language questions into a single read-only SQL SELECT "
    "statement for the schema below. Output ONLY the SQL — no explanation, no markdown "
    "fences, no trailing semicolon.\n\n{schema}"
)

SUMMARIZE_SYSTEM_PROMPT = (
    "You explain SQL query results in one or two plain-language sentences for a "
    "non-technical business user. Be specific with numbers. Do not mention SQL or "
    "the word 'query'. The rows below are read-only results already returned by the "
    "database — never claim that any data was added, changed, or deleted; only "
    "describe what these rows show."
)


def check_intent_node(state: DbChatState) -> DbChatState:
    blocked = bool(_WRITE_INTENT_RE.search(state["question"]))
    return {**state, "error": "write_intent" if blocked else None}


def refuse_write_node(state: DbChatState) -> DbChatState:
    return {**state, "answer": REFUSAL_MESSAGE, "sql": "", "columns": [], "rows": []}


def route_after_intent(state: DbChatState) -> str:
    return "blocked" if state.get("error") == "write_intent" else "allowed"


def generate_sql_node(state: DbChatState) -> DbChatState:
    retries = state.get("retries", 0)
    prior_error = state.get("error")
    if prior_error:
        retries += 1

    prompt = f"Question: {state['question']}"
    if prior_error:
        prompt += (
            f"\n\nYour previous attempt failed with this error, fix it:\n{prior_error}\n"
            f"Previous SQL: {state.get('sql', '')}"
        )

    llm = get_llm()
    response = llm.invoke(
        [
            ("system", GENERATE_SYSTEM_PROMPT.format(schema=get_schema_description())),
            ("human", prompt),
        ]
    )
    return {**state, "sql": response.content, "retries": retries}


def validate_sql_node(state: DbChatState) -> DbChatState:
    try:
        clean_sql = validate_and_prepare_sql(state["sql"], state["dialect"])
        return {**state, "sql": clean_sql, "error": None}
    except SqlValidationError as exc:
        return {**state, "error": str(exc)}


def execute_sql_node(state: DbChatState) -> DbChatState:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(state["sql"]))
            columns = list(result.keys())
            rows = [dict(row._mapping) for row in result.fetchmany(MAX_ROWS)]
        return {**state, "columns": columns, "rows": rows, "error": None}
    except Exception as exc:  # noqa: BLE001 - surfaced to the LLM for self-correction
        return {**state, "error": f"Database error: {exc}"}


def summarize_node(state: DbChatState) -> DbChatState:
    if not state["rows"]:
        return {**state, "answer": "That query didn't match any rows."}

    preview = state["rows"][:20]
    llm = get_llm()
    response = llm.invoke(
        [
            ("system", SUMMARIZE_SYSTEM_PROMPT),
            (
                "human",
                f"Question: {state['question']}\n"
                f"Columns: {state['columns']}\n"
                f"Rows ({len(state['rows'])} total, showing up to 20): {preview}",
            ),
        ]
    )
    return {**state, "answer": response.content}


def give_up_node(state: DbChatState) -> DbChatState:
    return {
        **state,
        "answer": "I couldn't build a valid query for that question. Try rephrasing it, "
        "or ask about departments, employees, products, or orders.",
        "columns": [],
        "rows": [],
    }


def route_after_check(state: DbChatState) -> str:
    if not state.get("error"):
        return "ok"
    return "retry" if state.get("retries", 0) < MAX_RETRIES else "give_up"
