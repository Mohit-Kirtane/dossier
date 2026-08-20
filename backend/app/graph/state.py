from typing import TypedDict


class SourceChunk(TypedDict):
    source: str
    content: str
    score: float


class GraphState(TypedDict):
    question: str
    chat_history: list[dict]
    sources: list[SourceChunk]
    answer: str
