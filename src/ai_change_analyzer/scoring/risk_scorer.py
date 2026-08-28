from typing import Any

from ai_change_analyzer.graph.state import ChangeAnalysisState

CRITICALITY_SCORES = {
    "LOW": 3,
    "MEDIUM": 8,
    "HIGH": 15,
}

SEVERITY_POINTS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 4,
}

RECOVERY_TERMS = [
    "partial",
    "reconcile",
    "committed",
    "batch state",
    "data state",
    "recovery",
]

EXPECTED_TEST_AREAS = [
    ["successful", "normal"],
    ["deadlock"],
    ["three", "retry limit", "persistent"],
    ["rollback"],
    ["partial"],
    ["duplicate"],
    ["downstream"],
]

DATA_INTEGRITY_TERMS = [
    "duplicate",
    "partial commit",
    "inconsistent",
    "data corruption",
]

DOWNSTREAM_TERMS = [
    "downstream",
    "file generation",
    "notification",
]


def _factor(
    name: str,
    score: int,
    max_score: int,
    reason: str,
) -> dict[str, Any]:
    return {
        "factor": name,
        "score": score,
        "max_score": max_score,
        "reason": reason,
    }


def _risk_level(score: int) -> str:
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def calculate_risk_score(
    state: ChangeAnalysisState,
) -> dict[str, Any]:
    breakdown = []

    # 1. Application criticality — max 15
    criticality = (
        state["original_change"]
        .get("business_criticality", "MEDIUM")
        .upper()
    )
    criticality_score = CRITICALITY_SCORES.get(
        criticality,
        CRITICALITY_SCORES["MEDIUM"],
    )

    breakdown.append(
        _factor(
            "Application criticality",
            criticality_score,
            15,
            f"Business criticality is {criticality}.",
        )
    )

    # 2. Affected scope — max 10
    component_count = len(
        {
            finding["component"].lower()
            for finding in state.get("impact_findings", [])
        }
    )

    if component_count >= 4:
        scope_score = 10
    elif component_count >= 2:
        scope_score = 7
    elif component_count == 1:
        scope_score = 3
    else:
        scope_score = 0

    breakdown.append(
        _factor(
            "Affected scope",
            scope_score,
            10,
            f"{component_count} distinct impacted components identified.",
        )
    )

    # 3. Historical incidents — max 20
    incident_score = min(
        sum(
            SEVERITY_POINTS.get(
                document.metadata.get("severity", "").upper(),
                0,
            )
            for document in state.get("related_incidents", [])[:5]
        ),
        20,
    )

    breakdown.append(
        _factor(
            "Historical incidents",
            incident_score,
            20,
            "Based on severity of the five most relevant "
            "retrieved historical incidents.",
        )
    )

    # 4. Rollback quality — max 15
    rollback_plan = (
        state["original_change"]
        .get("rollback_plan", "")
        .lower()
    )
    recovery_coverage = sum(
        term in rollback_plan
        for term in RECOVERY_TERMS
    )

    if recovery_coverage == 0:
        rollback_score = 15
        rollback_reason = (
            "Rollback plan does not explain recovery of "
            "partially processed data or batches."
        )
    elif recovery_coverage <= 2:
        rollback_score = 8
        rollback_reason = (
            "Rollback plan contains partial recovery coverage."
        )
    else:
        rollback_score = 0
        rollback_reason = (
            "Rollback plan contains detailed recovery coverage."
        )

    breakdown.append(
        _factor(
            "Rollback quality",
            rollback_score,
            15,
            rollback_reason,
        )
    )

    # 5. Test coverage gaps — max 15
    testing_summary = (
        state["original_change"]
        .get("testing_summary", "")
        .lower()
    )

    covered_areas = sum(
        any(term in testing_summary for term in area)
        for area in EXPECTED_TEST_AREAS
    )
    missing_areas = len(EXPECTED_TEST_AREAS) - covered_areas
    test_score = round(
        missing_areas / len(EXPECTED_TEST_AREAS) * 15
    )

    breakdown.append(
        _factor(
            "Test coverage gaps",
            test_score,
            15,
            f"{missing_areas} of {len(EXPECTED_TEST_AREAS)} expected "
            "risk-oriented test areas are not covered by the "
            "submitted testing summary.",
        )
    )

    # 6. Data-integrity exposure — max 15
    risk_text = " ".join(
        f"{risk.get('title', '')} {risk.get('description', '')}".lower()
        for risk in state.get("identified_risks", [])
    )

    has_data_integrity_risk = any(
        term in risk_text
        for term in DATA_INTEGRITY_TERMS
    )
    data_integrity_score = (
        15 if has_data_integrity_risk else 0
    )

    breakdown.append(
        _factor(
            "Data integrity exposure",
            data_integrity_score,
            15,
            (
                "Evidence-backed risks include duplicate, "
                "partial-commit, inconsistent-state, or "
                "data-corruption concerns."
                if has_data_integrity_risk
                else "No explicit data-integrity risk identified."
            ),
        )
    )

    # 7. Downstream dependencies — max 10
    architecture_text = " ".join(
        document.page_content.lower()
        for document in state.get("architecture_evidence", [])
    )

    downstream_matches = sum(
        term in architecture_text
        for term in DOWNSTREAM_TERMS
    )

    if downstream_matches >= 2:
        downstream_score = 10
    elif downstream_matches == 1:
        downstream_score = 5
    else:
        downstream_score = 0

    breakdown.append(
        _factor(
            "Downstream dependencies",
            downstream_score,
            10,
            f"{downstream_matches} downstream dependency signals "
            "found in architecture evidence.",
        )
    )

    total_score = sum(
        factor["score"]
        for factor in breakdown
    )

    return {
        "risk_score": total_score,
        "overall_risk": _risk_level(total_score),
        "risk_breakdown": breakdown,
    }