import json
import re

from ai_change_analyzer.graph.workflow import build_graph


def evaluate_reference_case() -> None:
    with open(
        "data/changes/new_change.json",
        encoding="utf-8",
    ) as file:
        change = json.load(file)

    graph = build_graph()

    result = graph.invoke(
        {
            "original_change": change,
        }
    )

    report = result.get("final_report")

    if not report:
        print("FAIL: Final report was not generated.")
        return

    retrieved_incident_ids = {
        document.metadata["incident_id"]
        for document in result["related_incidents"]
    }

    mentioned_incident_ids = set()

    for risk in report["identified_risks"]:
        for evidence in risk["evidence"]:
            mentioned_incident_ids.update(
                re.findall(r"INC\d+", evidence)
            )

    fabricated_incidents = (
        mentioned_incident_ids - retrieved_incident_ids
    )

    checks = {
        "Overall risk is HIGH":
            report["overall_risk"] == "HIGH",

        "Risk score is at least 60":
            report["risk_score"] >= 60,

        "At least one risk identified":
            len(report["identified_risks"]) > 0,

        "Regression tests generated":
            len(report["recommended_tests"]) > 0,

        "Missing information identified":
            len(report["missing_information"]) > 0,

        "Historical incidents retrieved":
            len(report["related_incidents"]) > 0,

        "No fabricated incident IDs":
            len(fabricated_incidents) == 0,
    }

    print("\nREFERENCE CASE EVALUATION")
    print("=" * 60)

    passed = 0

    for name, success in checks.items():
        status = "PASS" if success else "FAIL"
        print(f"{status}: {name}")

        if success:
            passed += 1

    print("\nRESULT")
    print(f"{passed}/{len(checks)} checks passed")

    if fabricated_incidents:
        print(
            "\nFabricated incident IDs detected:",
            ", ".join(sorted(fabricated_incidents)),
        )

    if passed == len(checks):
        print("\nREFERENCE CASE: PASS")
    else:
        print("\nREFERENCE CASE: FAIL")


if __name__ == "__main__":
    evaluate_reference_case()