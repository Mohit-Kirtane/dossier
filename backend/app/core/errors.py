import logging

from openai import RateLimitError

logger = logging.getLogger("app")


def friendly_llm_error(exc: Exception) -> str:
    logger.exception("LLM call failed")
    if isinstance(exc, RateLimitError):
        return "The AI provider's request quota is exhausted right now. Please try again later."
    return "The AI provider is temporarily unavailable. Please try again in a moment."
