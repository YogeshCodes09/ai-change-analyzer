from typing import Any, TypedDict

from langchain_core.documents import Document


class ChangeAnalysisState(TypedDict, total=False):
    original_change: dict[str, Any]

    change_summary: str
    affected_components: list[str]
    search_queries: dict[str, str]

    retrieved_sop: list[Document]
    related_incidents: list[Document]
    related_changes: list[Document]
    architecture_evidence: list[Document]

    evidence_status: str

    impact_findings: list[dict[str, Any]]
    identified_risks: list[dict[str, Any]]
    recommended_tests: list[dict[str, Any]]

    risk_score: int
    overall_risk: str
    risk_breakdown: list[dict[str, Any]]

    missing_information: list[str]

    final_report: dict[str, Any]