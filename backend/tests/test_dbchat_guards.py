import pytest

from app.dbchat.nodes import check_intent_node
from app.dbchat.sql_guard import SqlValidationError, validate_and_prepare_sql


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM demo_employees",
        "UPDATE demo_employees SET salary = 0",
        "DROP TABLE demo_employees",
        "SELECT * FROM demo_employees; DROP TABLE demo_employees",
        "INSERT INTO demo_employees (name) VALUES ('x')",
    ],
)
def test_rejects_write_statements(sql):
    with pytest.raises(SqlValidationError):
        validate_and_prepare_sql(sql, "sqlite")


def test_rejects_unknown_tables():
    with pytest.raises(SqlValidationError):
        validate_and_prepare_sql("SELECT * FROM documents", "sqlite")


def test_adds_limit_when_missing():
    sql = validate_and_prepare_sql("SELECT * FROM demo_employees", "sqlite")
    assert "LIMIT 200" in sql.upper()


def test_clamps_oversized_limit():
    sql = validate_and_prepare_sql("SELECT * FROM demo_employees LIMIT 5000", "sqlite")
    assert "LIMIT 200" in sql.upper()


def test_allows_ordinary_select():
    sql = validate_and_prepare_sql(
        "SELECT d.name, COUNT(*) FROM demo_employees e "
        "JOIN demo_departments d ON e.department_id = d.id GROUP BY d.name",
        "sqlite",
    )
    assert sql.upper().startswith("SELECT")


@pytest.mark.parametrize(
    "question",
    [
        "Delete all rows from demo_employees",
        "Please update everyone's salary to 0",
        "Drop the employees table",
        "Can you remove Ava Chen from the employees table",
    ],
)
def test_intent_guard_blocks_write_requests(question):
    result = check_intent_node({"question": question})
    assert result["error"] == "write_intent"


@pytest.mark.parametrize(
    "question",
    [
        "How many employees were hired last year?",
        "Which employees were let go this quarter?",
        "Show me all products in the Subscription category",
    ],
)
def test_intent_guard_allows_read_questions(question):
    result = check_intent_node({"question": question})
    assert result["error"] is None
