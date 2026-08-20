import uuid

from langchain_core.documents import Document

from app.core.vectorstore import add_documents
from app.graph.nodes import retrieve_node
from app.graph.workflow import run_workflow


def _seed_document(document_id: str, filename: str, text: str) -> None:
    add_documents(
        [Document(page_content=text, metadata={"document_id": document_id, "source": filename})]
    )


def _state(question: str, document_id: str | None) -> dict:
    return {
        "question": question,
        "chat_history": [],
        "document_id": document_id,
        "sources": [],
        "answer": "",
    }


def setup_module(module):
    module.doc_a = str(uuid.uuid4())
    module.doc_b = str(uuid.uuid4())
    _seed_document(
        module.doc_a,
        "remote-work-policy.txt",
        "Acme Corp remote work policy. Employees may work remotely up to 3 days per week.",
    )
    _seed_document(
        module.doc_b,
        "expense-policy.txt",
        "Acme Corp expense policy. Meals are reimbursed up to $50 per day while traveling.",
    )


def test_retrieval_scoped_to_document_id_excludes_other_documents():
    result = retrieve_node(_state("How much can I be reimbursed for meals?", doc_a))
    # The real answer lives in doc_b - scoping to doc_a must not leak it in.
    assert all(s["source"] != "expense-policy.txt" for s in result["sources"])


def test_retrieval_scoped_to_document_id_finds_its_own_content():
    result = retrieve_node(_state("How much can I be reimbursed for meals?", doc_b))
    assert any(s["source"] == "expense-policy.txt" for s in result["sources"])


def test_overview_question_bypasses_threshold_when_document_scoped():
    result = retrieve_node(_state("What is this document about?", doc_a))
    assert result["sources"]
    assert all(s["source"] == "remote-work-policy.txt" for s in result["sources"])


def test_overview_question_without_document_scope_can_still_return_nothing():
    # Without a selected document there's no safe corpus to skip the threshold
    # against, so the existing NO_CONTEXT behavior is preserved.
    result = retrieve_node(_state("What is this document about?", None))
    assert result["sources"] == []


def test_workflow_document_scoped_path_compiles_and_runs_with_no_llm_call():
    # Exercises the compiled StateGraph end to end (not just the node function)
    # with document_id threaded through - catches state/graph wiring bugs that
    # node-level tests alone would miss. Scoped to doc_a with a question whose
    # answer only lives in doc_b, so retrieval finds nothing and the graph
    # takes the no-LLM-call end_no_context path.
    result = run_workflow("How much can I be reimbursed for meals?", [], document_id=doc_a)
    assert result["sources"] == []
    assert "couldn't find" in result["answer"].lower()
