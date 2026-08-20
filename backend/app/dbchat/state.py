from typing import TypedDict


class DbChatState(TypedDict):
    question: str
    dialect: str
    sql: str
    error: str | None
    retries: int
    columns: list[str]
    rows: list[dict]
    answer: str
