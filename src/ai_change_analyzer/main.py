import argparse
import json
from pathlib import Path

from ai_change_analyzer.graph.workflow import build_graph

DEFAULT_CHANGE_PATH = Path("data/changes/new_change.json")


def load_change(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def print_items(title: str, items: list[str]) -> None:
    print(f"\n{title}")
    for item in items:
        print(f"- {item}")


def print_report(report: dict) -> None:
    print("\n" + "=" * 70)
    print("AI CHANGE ANALYZER")
    print("=" * 70)

    print(f"\nChange ID: {report['change_id']}")
    print(f"\nCHANGE SUMMARY\n{report['change_summary']}")
    print(
        f"\nOVERALL RISK\n"
        f"{report['overall_risk']} ({report['risk_score']}/100)"
    )

    print_items(
        "POTENTIALLY AFFECTED COMPONENTS",
        report["affected_components"],
    )
    print_items(
        "RELATED HISTORICAL INCIDENTS",
        report["related_incidents"],
    )

    print("\nIDENTIFIED RISKS")
    for index, risk in enumerate(report["identified_risks"], start=1):
        print(f"\n{index}. [{risk['severity']}] {risk['title']}")
        print(f"   {risk['description']}")
        print("   Evidence:")
        for evidence in risk["evidence"]:
            print(f"   - {evidence}")
        print(f"   Reasoning: {risk['reasoning']}")

    print("\nRECOMMENDED REGRESSION TESTS")
    for index, test in enumerate(report["recommended_tests"], start=1):
        print(f"\n{index}. {test['title']}")
        print(f"   Scenario: {test['scenario']}")
        print(f"   Expected Result: {test['expected_result']}")

    print_items(
        "MISSING INFORMATION",
        report["missing_information"],
    )

    print("\nRISK SCORE BREAKDOWN")
    for factor in report["risk_breakdown"]:
        print(
            f"- {factor['factor']}: "
            f"{factor['score']}/{factor['max_score']}"
        )
        print(f"  {factor['reason']}")

    print(f"\nRECOMMENDATION\n{report['recommendation']}")
    print("\n" + "=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a proposed production change using enterprise evidence."
    )
    parser.add_argument(
        "change_file",
        nargs="?",
        default=str(DEFAULT_CHANGE_PATH),
        help="Path to the proposed change JSON file.",
    )
    args = parser.parse_args()

    change_path = Path(args.change_file)

    if not change_path.exists():
        raise FileNotFoundError(f"Change file not found: {change_path}")

    result = build_graph().invoke(
        {"original_change": load_change(change_path)}
    )

    report = result.get("final_report")

    if report:
        print_report(report)
        return

    print("\nAnalysis stopped due to insufficient evidence.")
    print_items(
        "Missing information:",
        result.get("missing_information", []),
    )


if __name__ == "__main__":
    main()