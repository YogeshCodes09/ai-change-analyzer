from langchain_core.documents import Document

from ai_change_analyzer.scoring.risk_scorer import calculate_risk_score


def build_state(
    rollback_plan: str,
    testing_summary: str,
) -> dict:
    return {
        "original_change": {
            "business_criticality": "HIGH",
            "rollback_plan": rollback_plan,
            "testing_summary": testing_summary,
        },
        "impact_findings": [
            {
                "component": "Card Production Database",
            },
            {
                "component": "Batch Processor",
            },
        ],
        "related_incidents": [
            Document(
                page_content="Database deadlock",
                metadata={"severity": "HIGH"},
            ),
            Document(
                page_content="Duplicate processing",
                metadata={"severity": "HIGH"},
            ),
        ],
        "identified_risks": [
            {
                "title": "Duplicate processing",
                "description": "Partial commit may create duplicate data.",
            }
        ],
        "architecture_evidence": [
            Document(
                page_content=(
                    "Card Production depends on downstream "
                    "file generation and notification services."
                )
            )
        ],
    }


def test_high_risk_change_scores_high() -> None:
    state = build_state(
        rollback_plan="Deploy previous application version.",
        testing_summary="Test successful processing and deadlock recovery.",
    )

    result = calculate_risk_score(state)

    assert result["overall_risk"] == "HIGH"
    assert result["risk_score"] >= 60


def test_better_controls_reduce_risk_score() -> None:
    weak_state = build_state(
        rollback_plan="Deploy previous application version.",
        testing_summary="Test successful processing.",
    )

    strong_state = build_state(
        rollback_plan=(
            "Restore previous version, reconcile partially processed "
            "batches, verify committed records, validate batch state, "
            "and complete recovery."
        ),
        testing_summary=(
            "Test normal successful processing, deadlock handling, "
            "persistent three retry limit, rollback, partial commits, "
            "duplicate prevention and downstream processing."
        ),
    )

    weak_result = calculate_risk_score(weak_state)
    strong_result = calculate_risk_score(strong_state)

    assert strong_result["risk_score"] < weak_result["risk_score"]