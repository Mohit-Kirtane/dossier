from app.db import policy_models  # noqa: F401 - registers tables on Base.metadata
from app.db.session import SessionLocal, init_db
from app.rbac.nodes import retrieve_node, route_after_retrieve
from app.rbac.seed import seed_policy_documents
from app.rbac.workflow import run_workflow


def setup_module(module):
    init_db()
    with SessionLocal() as session:
        seed_policy_documents(session)


def _state(question: str, role: str) -> dict:
    return {"question": question, "role": role, "sources": [], "restricted": False, "answer": ""}


def test_hr_role_can_see_compensation_policy():
    result = retrieve_node(_state("What are the salary bands for each level?", "hr"))
    assert result["sources"]
    assert any("Compensation" in s["source"] for s in result["sources"])
    assert result["restricted"] is False


def test_executive_role_can_see_compensation_policy():
    result = retrieve_node(_state("What are the salary bands for each level?", "executive"))
    assert result["sources"]


def test_employee_role_is_blocked_from_compensation_policy():
    result = retrieve_node(_state("What are the salary bands for each level?", "employee"))
    assert result["sources"] == []
    assert result["restricted"] is True


def test_manager_role_is_blocked_from_compensation_policy():
    result = retrieve_node(_state("What are the salary bands for each level?", "manager"))
    assert result["sources"] == []
    assert result["restricted"] is True


def test_employee_role_is_blocked_from_ma_disclosure_policy():
    result = retrieve_node(_state("When is the trading blackout window before earnings?", "employee"))
    assert result["sources"] == []
    assert result["restricted"] is True


def test_executive_role_can_see_ma_disclosure_policy():
    result = retrieve_node(_state("When is the trading blackout window before earnings?", "executive"))
    assert result["sources"]


def test_employee_role_can_see_pto_policy():
    result = retrieve_node(_state("How many PTO days do I accrue per year?", "employee"))
    assert result["sources"]
    assert any("PTO" in s["source"] for s in result["sources"])


def test_all_roles_can_see_security_policy():
    for role in ["employee", "manager", "hr", "executive"]:
        result = retrieve_node(_state("How are data classification levels defined?", role))
        assert result["sources"], f"role {role} should see the security policy"


def test_unrelated_question_is_not_restricted():
    result = retrieve_node(_state("What is the capital of France?", "employee"))
    assert result["sources"] == []
    assert result["restricted"] is False


def test_route_after_retrieve():
    assert route_after_retrieve({"sources": [{"x": 1}], "restricted": False}) == "generate"
    assert route_after_retrieve({"sources": [], "restricted": True}) == "restricted"
    assert route_after_retrieve({"sources": [], "restricted": False}) == "no_context"


def test_workflow_restricted_path_compiles_and_runs_with_no_llm_call():
    # Exercises the actual compiled StateGraph, not just the node function in
    # isolation - this is what catches graph-construction bugs (e.g. a node
    # name colliding with a state key) that node-level tests can't see.
    result = run_workflow("What are the salary bands for each level?", "employee")
    assert result["restricted"] is True
    assert "outside what the employee role can access" in result["answer"]


def test_workflow_no_context_path_compiles_and_runs_with_no_llm_call():
    result = run_workflow("What is the capital of France?", "employee")
    assert result["restricted"] is False
    assert result["sources"] == []
    assert "couldn't find" in result["answer"].lower()
