from langgraph.graph import END, START, StateGraph

from ai_change_analyzer.graph.nodes import (
    analyze_impact,
    assess_risk,
    check_evidence,
    generate_final_report,
    generate_tests,
    handle_insufficient_evidence,
    retrieve_architecture,
    retrieve_incidents,
    retrieve_similar_changes,
    retrieve_sop,
    score_risk,
    understand_change,
)
from ai_change_analyzer.graph.state import ChangeAnalysisState

RETRIEVAL_NODES = (
    "retrieve_incidents",
    "retrieve_sop",
    "retrieve_similar_changes",
    "retrieve_architecture",
)


def route_by_evidence(state: ChangeAnalysisState) -> str:
    return (
        "insufficient"
        if state["evidence_status"] == "insufficient"
        else "continue"
    )


def build_graph():
    builder = StateGraph(ChangeAnalysisState)

    nodes = {
        "understand_change": understand_change,
        "retrieve_incidents": retrieve_incidents,
        "retrieve_sop": retrieve_sop,
        "retrieve_similar_changes": retrieve_similar_changes,
        "retrieve_architecture": retrieve_architecture,
        "check_evidence": check_evidence,
        "handle_insufficient_evidence": handle_insufficient_evidence,
        "analyze_impact": analyze_impact,
        "assess_risk": assess_risk,
        "generate_tests": generate_tests,
        "score_risk": score_risk,
        "generate_final_report": generate_final_report,
    }

    for name, node in nodes.items():
        builder.add_node(name, node)

    builder.add_edge(START, "understand_change")

    # Parallel retrieval
    for node in RETRIEVAL_NODES:
        builder.add_edge("understand_change", node)

    # Fan-in after all retrieval branches complete
    builder.add_edge(
        list(RETRIEVAL_NODES),
        "check_evidence",
    )

    builder.add_conditional_edges(
        "check_evidence",
        route_by_evidence,
        {
            "continue": "analyze_impact",
            "insufficient": "handle_insufficient_evidence",
        },
    )

    builder.add_edge(
        "handle_insufficient_evidence",
        END,
    )

    # Normal analysis path
    normal_flow = (
        ("analyze_impact", "assess_risk"),
        ("assess_risk", "generate_tests"),
        ("generate_tests", "score_risk"),
        ("score_risk", "generate_final_report"),
        ("generate_final_report", END),
    )

    for source, target in normal_flow:
        builder.add_edge(source, target)

    return builder.compile()