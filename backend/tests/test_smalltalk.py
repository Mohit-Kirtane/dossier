import pytest

from app.core.smalltalk import is_smalltalk


@pytest.mark.parametrize(
    "question",
    [
        "hi",
        "Hi!",
        "hello",
        "hey there",
        "heyyy",
        "yo",
        "howdy",
        "good morning",
        "Good Evening!",
        "what can you do?",
        "what do you do",
        "who are you",
        "how does this work?",
        "what is this app",
        "help me",
        "can you help",
    ],
)
def test_is_smalltalk_true(question):
    assert is_smalltalk(question) is True


@pytest.mark.parametrize(
    "question",
    [
        "How many vacation days do employees get?",
        "Which department has the highest total salary cost?",
        "What are the salary bands for each level?",
        "hire me a data engineer",
        "high salary employees in engineering",
    ],
)
def test_is_smalltalk_false(question):
    assert is_smalltalk(question) is False


def test_document_workflow_answers_smalltalk_with_zero_llm_calls():
    from app.graph.nodes import SMALLTALK_ANSWER
    from app.graph.workflow import run_workflow

    result = run_workflow("hi", [])
    assert result["answer"] == SMALLTALK_ANSWER
    assert result["sources"] == []


def test_database_workflow_answers_smalltalk_with_zero_llm_calls():
    from app.dbchat.nodes import SMALLTALK_ANSWER
    from app.dbchat.workflow import run_workflow

    result = run_workflow("hello")
    assert result["answer"] == SMALLTALK_ANSWER
    assert result["sql"] == ""
    assert result["rows"] == []


def test_policy_workflow_answers_smalltalk_with_zero_llm_calls():
    from app.rbac.nodes import SMALLTALK_ANSWER
    from app.rbac.workflow import run_workflow

    result = run_workflow("what can you do?", "employee")
    assert result["answer"] == SMALLTALK_ANSWER
    assert result["restricted"] is False
