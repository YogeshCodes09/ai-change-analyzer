from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from ai_change_analyzer.graph.state import ChangeAnalysisState
from ai_change_analyzer.models.change_understanding import ChangeUnderstanding
from ai_change_analyzer.models.final_report import FinalChangeReport
from ai_change_analyzer.models.impact import ImpactAnalysis
from ai_change_analyzer.models.recommendation import TestRecommendations
from ai_change_analyzer.models.risk import RiskAnalysis
from ai_change_analyzer.retrieval.retriever import search
from ai_change_analyzer.scoring.risk_scorer import calculate_risk_score

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

change_understanding_model = model.with_structured_output(
    ChangeUnderstanding,
    method="json_schema",
)

impact_model = model.with_structured_output(
    ImpactAnalysis,
    method="json_schema",
)

risk_model = model.with_structured_output(
    RiskAnalysis,
    method="json_schema",
)

test_model = model.with_structured_output(
    TestRecommendations,
    method="json_schema",
)


RECOMMENDATIONS = {
    "HIGH": (
        "Additional testing and clarification of rollback, recovery, "
        "and data-integrity controls are required before production deployment."
    ),
    "MEDIUM": (
        "The change may proceed only after the identified risk gaps "
        "and missing information are reviewed."
    ),
    "LOW": (
        "The change currently presents limited identified risk, "
        "subject to normal change-management approval."
    ),
}


def _format_documents(documents: list[Document]) -> str:
    return "\n\n".join(document.page_content for document in documents)


def _dump_models(items: list) -> list[dict]:
    return [item.model_dump() for item in items]


def _merge_missing(
    state: ChangeAnalysisState,
    new_items: list[str],
) -> list[str]:
    return list(
        dict.fromkeys(
            state.get("missing_information", []) + new_items
        )
    )


def understand_change(state: ChangeAnalysisState) -> dict:
    result = change_understanding_model.invoke(
        f"""
Analyze the following proposed production change.

Your task is only to understand the change and prepare focused
search queries for retrieving supporting evidence.

Create a separate search query for:
- historical incidents
- historical changes
- SOP requirements
- product architecture and dependencies

Do not assess overall risk.
Do not invent system components that are not reasonably implied
by the change.

Proposed change:

{state["original_change"]}
"""
    )

    return {
        "change_summary": result.change_summary,
        "affected_components": result.affected_components,
        "search_queries": result.search_queries.model_dump(),
    }


def _retrieve_documents(
    query: str,
    source_type: str,
    k: int,
) -> list[Document]:
    documents = []

    for document, score in search(
        query=query,
        source_type=source_type,
        k=k,
    ):
        document.metadata["retrieval_score"] = score
        documents.append(document)

    return documents


def retrieve_incidents(state: ChangeAnalysisState) -> dict:
    return {
        "related_incidents": _retrieve_documents(
            state["search_queries"]["incident"],
            "incident",
            8,
        )
    }


def retrieve_similar_changes(state: ChangeAnalysisState) -> dict:
    return {
        "related_changes": _retrieve_documents(
            state["search_queries"]["change"],
            "change",
            5,
        )
    }


def retrieve_sop(state: ChangeAnalysisState) -> dict:
    return {
        "retrieved_sop": _retrieve_documents(
            state["search_queries"]["sop"],
            "sop",
            7,
        )
    }


def retrieve_architecture(state: ChangeAnalysisState) -> dict:
    return {
        "architecture_evidence": _retrieve_documents(
            state["search_queries"]["product"],
            "product",
            7,
        )
    }


def check_evidence(state: ChangeAnalysisState) -> dict:
    evidence = {
        "related_incidents": "No relevant historical incidents were found.",
        "related_changes": "No similar historical changes were found.",
        "retrieved_sop": "No relevant SOP evidence was found.",
        "architecture_evidence": "No relevant architecture evidence was found.",
    }

    missing_information = [
        message
        for key, message in evidence.items()
        if not state.get(key)
    ]

    has_core_evidence = bool(
        state.get("retrieved_sop")
        or state.get("architecture_evidence")
    )

    return {
        "evidence_status": (
            "sufficient" if has_core_evidence else "insufficient"
        ),
        "missing_information": missing_information,
    }


def handle_insufficient_evidence(
    state: ChangeAnalysisState,
) -> dict:
    return {
        "impact_findings": [],
        "identified_risks": [],
        "recommended_tests": [],
    }


def analyze_impact(state: ChangeAnalysisState) -> dict:
    result = impact_model.invoke(
        f"""
Analyze the potential technical impact of the proposed change.

CHANGE:
{state["change_summary"]}

RETRIEVED SOP EVIDENCE:
{_format_documents(state["retrieved_sop"])}

RETRIEVED ARCHITECTURE EVIDENCE:
{_format_documents(state["architecture_evidence"])}

Rules:

1. Base findings only on the supplied evidence.
2. Clearly separate evidence from inference.
3. Do not invent components or dependencies.
4. If important information cannot be confirmed, add it to
   missing_information.
5. Do not assign an overall risk rating yet.
6. The source field must identify whether the finding came from
   SOP evidence or architecture evidence.
"""
    )

    return {
        "impact_findings": _dump_models(result.findings),
        "missing_information": _merge_missing(
            state,
            result.missing_information,
        ),
    }


def assess_risk(state: ChangeAnalysisState) -> dict:
    result = risk_model.invoke(
        f"""
Identify potential operational and technical risks for the
proposed production change.

CHANGE:
{state["change_summary"]}

IMPACT FINDINGS:
{state["impact_findings"]}

RELATED HISTORICAL INCIDENTS:
{_format_documents(state["related_incidents"])}

RELATED HISTORICAL CHANGES:
{_format_documents(state["related_changes"])}

RELEVANT SOP EVIDENCE:
{_format_documents(state["retrieved_sop"])}

Rules:

1. Every risk must be supported by the supplied evidence.
2. Do not invent incidents or historical failures.
3. Evidence should reference incident IDs, change IDs, or SOP
   sections where possible.
4. Clearly explain the reasoning connecting the evidence to the risk.
5. Severity describes the consequence if the risk occurs.
6. Do NOT calculate the overall change risk rating.
7. If important information is missing, add it to missing_information.
8. Avoid duplicate risks that describe the same underlying failure.
"""
    )

    return {
        "identified_risks": _dump_models(result.risks),
        "missing_information": _merge_missing(
            state,
            result.missing_information,
        ),
    }


def generate_tests(state: ChangeAnalysisState) -> dict:
    result = test_model.invoke(
        f"""
Generate focused regression test scenarios for the proposed
production change.

CHANGE:
{state["change_summary"]}

IMPACT FINDINGS:
{state["impact_findings"]}

IDENTIFIED RISKS:
{state["identified_risks"]}

Rules:

1. Every test must address one or more identified risks.
2. Include both successful and failure scenarios.
3. Include retry, rollback, duplicate-prevention and downstream
   processing scenarios when supported by the identified risks.
4. Expected results must be specific and testable.
5. Do not invent unrelated functionality.
6. Avoid duplicate test scenarios.
"""
    )

    return {
        "recommended_tests": _dump_models(result.tests),
    }


def score_risk(state: ChangeAnalysisState) -> dict:
    return calculate_risk_score(state)


def generate_final_report(
    state: ChangeAnalysisState,
) -> dict:
    report = FinalChangeReport(
        change_id=state["original_change"]["change_id"],
        change_summary=state["change_summary"],
        overall_risk=state["overall_risk"],
        risk_score=state["risk_score"],
        affected_components=state["affected_components"],
        related_incidents=[
            document.metadata["incident_id"]
            for document in state["related_incidents"]
        ],
        identified_risks=state["identified_risks"],
        recommended_tests=state["recommended_tests"],
        missing_information=state["missing_information"],
        risk_breakdown=state["risk_breakdown"],
        recommendation=RECOMMENDATIONS[state["overall_risk"]],
    )

    return {
        "final_report": report.model_dump(),
    }