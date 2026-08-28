from langchain_core.documents import Document

from ai_change_analyzer.graph.nodes import check_evidence
from ai_change_analyzer.graph.workflow import route_by_evidence


def test_insufficient_evidence_route() -> None:
    state = {
        "related_incidents": [],
        "related_changes": [],
        "retrieved_sop": [],
        "architecture_evidence": [],
    }

    result = check_evidence(state)

    state.update(result)

    assert result["evidence_status"] == "insufficient"
    assert route_by_evidence(state) == "insufficient"


def test_sufficient_evidence_route() -> None:
    state = {
        "related_incidents": [],
        "related_changes": [],
        "retrieved_sop": [
            Document(
                page_content="Retry must verify batch state."
            )
        ],
        "architecture_evidence": [
            Document(
                page_content="Batch Processor uses the database."
            )
        ],
    }

    result = check_evidence(state)

    state.update(result)

    assert result["evidence_status"] == "sufficient"
    assert route_by_evidence(state) == "continue"