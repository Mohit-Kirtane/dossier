from typing import TypedDict


class PolicyState(TypedDict):
    question: str
    role: str
    sources: list[dict]
    restricted: bool
    answer: str
