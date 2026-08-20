import re

_GREETING_RE = re.compile(
    r"^\s*((hi|hey+|hello)( there)?|yo|howdy|hiya|sup|what'?s up|"
    r"good\s+(morning|afternoon|evening))\s*[!.?]*\s*$",
    re.IGNORECASE,
)

_META_RE = re.compile(
    r"\b(what can you do|what do you do|who are you|what are you|"
    r"how does this work|how do you work|"
    r"what is this(?!\s+(document|pdf|file|upload))( (app|tool|thing))?|"
    r"help me|can you help|how (can|do) (i|you) use)\b",
    re.IGNORECASE,
)


def is_smalltalk(question: str) -> bool:
    """Greetings and capability questions never need retrieval, SQL, or an
    LLM call - answering them for free keeps quota for real questions and
    avoids nonsense (e.g. the SQL workflow trying to write a query for "hi")."""
    text = question.strip()
    return bool(_GREETING_RE.match(text) or _META_RE.search(text))
