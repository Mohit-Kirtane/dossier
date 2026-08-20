import re

import sqlglot
from sqlglot import exp

from app.dbchat.schema_info import ALLOWED_TABLES

MAX_ROWS = 200

_BLOCKED_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|attach|detach|pragma|vacuum|"
    r"replace|truncate|copy|into\s+outfile|call|exec|execute)\b",
    re.IGNORECASE,
)


class SqlValidationError(ValueError):
    pass


def _sqlglot_dialect(engine_dialect_name: str) -> str:
    return {"postgresql": "postgres", "sqlite": "sqlite"}.get(engine_dialect_name, engine_dialect_name)


_FENCE_RE = re.compile(r"```[a-zA-Z]*\n?(.*?)```", re.DOTALL)


def extract_sql_candidate(raw_text: str) -> str:
    """Pulls the SQL out of an LLM response that may include a fenced code
    block, surrounding prose, or just be the bare query."""
    match = _FENCE_RE.search(raw_text)
    candidate = match.group(1) if match else raw_text
    return candidate.strip().rstrip(";").strip()


def validate_and_prepare_sql(raw_sql: str, engine_dialect_name: str) -> str:
    """Parses, validates, and re-serializes a single read-only SQL statement.

    Raises SqlValidationError with a message safe to show the user (and to
    feed back to the LLM for a self-correction retry) if the query is not a
    single SELECT over the whitelisted demo tables.
    """
    dialect = _sqlglot_dialect(engine_dialect_name)
    sql = extract_sql_candidate(raw_sql)

    if not sql:
        raise SqlValidationError("The model returned an empty query.")
    if ";" in sql:
        raise SqlValidationError("Only a single SQL statement is allowed.")
    if _BLOCKED_KEYWORDS.search(sql):
        raise SqlValidationError("Only read-only SELECT queries are allowed.")

    try:
        tree = sqlglot.parse_one(sql, dialect=dialect)
    except Exception as exc:
        raise SqlValidationError(f"Could not parse the generated SQL: {exc}") from exc

    if not isinstance(tree, (exp.Select, exp.Union, exp.Subquery)):
        raise SqlValidationError("Only SELECT queries are allowed.")

    referenced_tables = {t.name.lower() for t in tree.find_all(exp.Table)}
    unknown = referenced_tables - set(ALLOWED_TABLES)
    if unknown:
        raise SqlValidationError(
            f"Query references unknown table(s): {', '.join(sorted(unknown))}. "
            f"Only these tables exist: {', '.join(ALLOWED_TABLES)}."
        )

    if isinstance(tree, exp.Select):
        existing_limit = tree.args.get("limit")
        if existing_limit is None:
            tree = tree.limit(MAX_ROWS)
        else:
            try:
                limit_value = int(existing_limit.expression.this)
                if limit_value > MAX_ROWS:
                    tree = tree.limit(MAX_ROWS)
            except (AttributeError, ValueError):
                tree = tree.limit(MAX_ROWS)

    return tree.sql(dialect=dialect)
